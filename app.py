from flask import Flask, render_template, request, redirect, url_for, session
import csv, io, random, string
import os
from datetime import datetime

def autosave_responses(responses):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = 'autosaves'
    os.makedirs(folder, exist_ok=True)
    filename = f'autosave_{timestamp}.csv'
    filepath = os.path.join(folder, filename)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Page', 'Task Index', 'Answer', 'Feedback', 'Response Time (s)', 'Time Limit', 'Base Avg Time', 'Raw'])

    timed_pages = [28, 34, 40, 46, 52, 58, 64, 70, 76]
    time_pair_map = {
        28: 4, 34: 6, 40: 8, 46: 10, 52: 12,
        58: 14, 64: 16, 70: 18, 76: 20
    }

    sorted_pages = sorted(responses.keys(), key=lambda x: int(x))

    for page in sorted_pages:
        page_num = int(page)
        resp = responses[page]

        if isinstance(resp, list):
            for entry in resp:
                task_index = int(entry.get('task_index', 1))
                time_limit = ''
                base_time = ''
                if page_num in timed_pages:
                    source_page = time_pair_map.get(page_num)
                    base_time = session.get(f'avg_time_page{source_page}', '')
                    try:
                        base_time = float(base_time)
                        time_limit = round(base_time * 1.4 * (0.95 ** (task_index - 1)), 3)
                        base_time = round(base_time, 3)
                    except:
                        time_limit = ''
                        base_time = ''
                writer.writerow([
                    page,
                    entry.get('task_index', ''),
                    entry.get('answer', ''),
                    entry.get('feedback', ''),
                    entry.get('task_time', ''),
                    time_limit,
                    base_time,
                    ''
                ])

        elif isinstance(resp, dict):
            if page_num in [22, 31, 37, 43, 49]:  # your letter grid pages
                letter_count = resp.get('letter_count', '0')
                writer.writerow([
                    page, '', '', '', '', '', '', f'letter_count: {letter_count}'
                ])
            else:
                flat_data = "; ".join([f"{k}: {v}" for k, v in resp.items()])
                writer.writerow([
                    page, '', '', '', '', '', '', flat_data
                ])

        else:
            writer.writerow([page, '', '', '', '', '', '', str(resp)])

    with open(filepath, 'w', newline='') as f:
        f.write(output.getvalue())




def clean(val):
    if isinstance(val, str):
        return val.strip()
    return val

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Conditional routing mapping:
# For example, after page 25, we check page 4’s performance.
condition_map = {
    4: (26, 32)   # If page 4 ≥ 40% correct, go to page 26; otherwise page 32.
}

###############################################################################
# FULL LIST OF 81 PAGES WITH UPDATED PAGE 14, 16, 18, 20, AND CONTINUOUS SCALE
###############################################################################
pages = [
    # Pages 1–3: Introductory
    {
    'page_number': 1,
    'title': 'Welcome to the Experiment',
    'content': """Hello! I'm Anastasiia Balukova, a master's student at Paris School of Economics, University of Paris 1 Panthéon-Sorbonne and University of Paris-Cité.
We are conducting this study to explore the relationship between socioeconomic status and academic performance. 
Your participation is crucial — this study is a part of my master thesis, and your responses will remain confidential.""",
    'type': 'info'
},
    {
    'page_number': 2,
    'title': 'Information Letter',
    'content': """Welcome! This study consists of 3 stages and will take approximately 20 to 30 minutes of your time.

<strong>Important:</strong> Participation is voluntary, and all your answers and your total performance will remain <strong>strictly anonymous</strong>. The collected data will be used uniquely for the purposes of this study and will only be available to my supervisor (Nina Guyon) and myself.

Note that once you complete a stage, you will not be able to go back to it. At any point during the study, you are free to leave or stay. Note that participation is entirely voluntary and does not imply any reward.

If you have any further questions regarding the study, or if you face any unexpected issues, feel free to contact me at <em>anastasiia.balukova@etu.univ-paris1.fr</em>.<br>
Supervised by Nina Guyon.

<br><br>If you agree to take part in this study, please check the box below and proceed.
""",
    'type': 'consent'
},
    {'page_number': 3, 'title': 'Before you begin', 'content': '''<div class="left-aligned-text">
<p><strong>The experiment is divided into three parts:</strong></p>

<p><u>Short Tasks</u><br>
You’ll complete a series of tasks involving math problems, reading comprehension, and vocabulary. Each type of task appears in three difficulty levels: Low, Medium, and High. These tasks have no time limit, but we ask that you answer as  <strong style="color: #d9534f;">accurately</strong> as possible. <strong style="color: #d9534f;">Please stay focused and avoid distractions</strong>.</p>

<p><u>Background Questions</u><br>
You’ll be asked a few questions about your personal background, education, and impressions. There are no right or wrong answers.</p>

<p><u>Timed Challenge</u><br>
In this final part, you’ll complete a series of quick tasks under time limit. These tasks will include a visible countdown timer and a progress bar that shows how much time is left.<br>
<strong style="color: #d9534f;">Important: Solve the problems mentally. Do not write down any calculations.</strong></p>

<p><strong>Ready to begin?</strong><br>
Once you click Next, your first Math task will begin.<br>
You will see a simple arithmetic problem (addition or subtraction). Solve the problem mentally and type your answer into the response box.</p>

<p><em>Example:</em><br>
8 - 5 = ?<br>
In the line below, type your answer:<br>
3</p>

<p>Click Next when you're ready to start.</p>
</div>''',
     'type': 'info'},

    # Page 4: Math Tasks Set 1
    {'page_number': 4, 'title': 'Math Tasks - Low difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': '7 - 4 =', 'correct_answer': '3'},
         {'question': '5 + 6 =', 'correct_answer': '11'},
         {'question': '9 - 3 =', 'correct_answer': '6'},
         {'question': '8 + 1 =', 'correct_answer': '9'},
         {'question': '4 + 8 =', 'correct_answer': '12'}
     ]},

    # Page 5: Instructions
    {'page_number': 5, 'title': 'Math Tasks Instructions', 'content': '''
<div class="info-container">
  <div class="info-section">
    <h4>Medium difficulty</h4>
    <p>You will see a two-step operation (addition, subtraction, multiplication, or division). Solve the problem mentally and type your answer into the response box.</p>
    <p><em>Example:</em></p>
    <p>38 + 30 − 11 = ?</p>
    <p>In the line below, type your answer:</p>
    <p><strong>57</strong></p>
  </div>

  <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

</div>
''',
 'type': 'info'},

    # Page 6: Math Tasks Set 2
    {'page_number': 6, 'title': 'Math Tasks - Medium difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': '23 + 17 - 5 =', 'correct_answer': '35'},
         {'question': '40 ÷ 5 + 6 =', 'correct_answer': '14'},
         {'question': '(50 - 20) × 2 =', 'correct_answer': '60'},
         {'question': '90 - (15 + 25) =', 'correct_answer': '50'},
         {'question': '(12 × 3) - (9 ÷ 3) =', 'correct_answer': '33'}
     ]},

    # Page 7: Instructions
    {'page_number': 7, 'title': 'Math Tasks Instructions', 'content': '''
<div class="info-container">
  <div class="info-section">
    <h4>High difficulty</h4>
    <p>You will see an equation where you must solve for x. Follow the steps to isolate x and find the correct answer.</p>
    <p><em>Example:</em></p>
    <p>Solve for x: 10x -13 = 37</p>
    <p>In the line below, type your answer:</p>
    <p><strong>5</strong></p>
  </div>

  <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

</div>
''',
 'type': 'info'},

    # Page 8: Math Tasks Set 3
    {'page_number': 8, 'title': 'Math Tasks - High difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': 'Solve for x: 3x + 5 = 20', 'correct_answer': '5'},
         {'question': 'Solve for x: (x ÷ 2) + 7 = 15', 'correct_answer': '16'},
         {'question': 'Solve for x: 4(x − 3) = 12', 'correct_answer': '6'},
         {'question': 'Solve for x: (2x + 4) ÷ 3 = 6', 'correct_answer': '7'},
         {'question': 'Solve for x: 5x − 2 = 3x + 8', 'correct_answer': '5'}
     ]},

    # Page 9: Instructions
    {'page_number': 9, 'title': 'Literature Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Low difficulty</h4>
            <p>You will read a short sentence or passage, then answer a question about a fact that is directly stated in the text.</p>
            <p><em>Example:</em></p>
            <p>"The boy drank a glass of water." What did the boy drink?</p>
            <p>a) Milk</p>
            <p>b) Juice</p>
            <p>c) Water</p>
            <p>d) Soda</p>
            <p>Choose the correct answer from the multiple-choice options. There is <strong style="color: #d9534f;">only ONE correct answer</strong>:</p>
            <p><strong>c) Water</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 10: Multiple Choice Set 1
    {'page_number': 10, 'title': 'Reading Tasks - Low difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Tom bought a red apple from the market. What did Tom buy?', 'options': ['a banana','a red apple','a loaf of bread','a watermelon'], 'correct_answer': 'a red apple'},
         {'question': 'Emma is reading a book under a tree. Where is Emma?', 'options': ['In the library','Under a tree','In the house','In the classroom'], 'correct_answer': 'Under a tree'},
         {'question': "Sarah's favorite color is blue. What is Sarah’s favorite color?", 'options': ['Green','Red','Blue','Yellow'], 'correct_answer': 'Blue'},
         {'question': 'John and Lisa went to the zoo to see the lions. What animal did they want to see?', 'options': ['Tigers','Elephants','Lions','Bears'], 'correct_answer': 'Lions'},
         {'question': 'The sun rises in the east. Where does the sun rise?', 'options': ['North','South','West','East'], 'correct_answer': 'East'}
     ]},

    # Page 11: Instructions
    {'page_number': 11, 'title': 'Reading Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Medium difficulty</h4>
            <p>You will read a short passage and answer a question that requires you to infer meaning. The answer won’t be stated directly, but you can figure it out based on the text.</p>
            <p><em>Example:</em></p>
            <p>"David turned off the alarm, stretched, and headed to the kitchen to make coffee." What time of day is it likely?</p>
            <p>a) Morning</p>
            <p>b) Afternoon</p>
            <p>c) Evening</p>
            <p>d) Midnight</p>
            <p>Select the most appropriate answer:</p>
            <p><strong>a) Morning</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 12: Multiple Choice Set 2
    {'page_number': 12, 'title': 'Reading Tasks - Medium difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Mike put on his raincoat and grabbed an umbrella before leaving the house. What was the weather likely like?', 'options': ['Sunny','Windy','Snowy','Rainy'], 'correct_answer': 'Rainy'},
         {'question': "Lena's hands were shaking as she stepped onto the stage to give her speech. How does Lena feel?", 'options': ['Excited','Nervous','Angry','Confident'], 'correct_answer': 'Nervous'},
         {'question': 'Anna missed the bus this morning, so she arrived late to work. Why was Anna late?', 'options': ['She overslept','She forgot the time','She missed the bus','She got lost'], 'correct_answer': 'She missed the bus'},
         {'question': 'Leo studied all night for his exam. When he got his results, he smiled. What can we infer about his exam?', 'options': ['He failed','He passed','He was nervous','He was unprepared'], 'correct_answer': 'He passed'},
         {'question': 'Jamal lit candles and turned off the lights before bringing out the cake. What event is likely happening?', 'options': ['A birthday','A wedding','A picnic','A graduation'], 'correct_answer': 'A birthday'}
     ]},

    # Page 13: Instructions
    {'page_number': 13, 'title': 'Reading Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>High difficulty</h4>
            <p>You will read a more complex passage and answer a question that requires deeper thinking. This may involve understanding the author’s tone, interpreting abstract ideas, or identifying their intent.</p>
            <p><em>Example:</em></p>
            <p>"The room fell silent as Nora entered, her reputation preceding her." What does this imply about Nora?</p>
            <p>a) She is well-known</p>
            <p>b) She is quiet</p>
            <p>c) She is invisible</p>
            <p>d) She is new to the group</p>
            <p>Select the most appropriate answer:</p>
            <p><strong>a) She is well-known</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 14: Multiple Choice Set 3 (UPDATED Passage Questions)
    {'page_number': 14, 'title': 'Reading Tasks - High difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Passage: "Although she had little money, Maria always made sure to donate a small amount to charity."\nQuestion: What does this tell us about Maria?',
          'options': ['She is selfish','She is generous','She is careless with money','She dislikes charity'],
          'correct_answer': 'She is generous'},
         {'question': 'Passage: "The hikers were running low on water, and the sun was beating down relentlessly."\nQuestion: What can we infer about the hikers’ situation?',
          'options': ['They are well-prepared','They are in a comfortable environment','They might be in danger','They are walking at night'],
          'correct_answer': 'They might be in danger'},
         {'question': 'Passage: "Even after his friends abandoned him, Jack continued to pursue his dream of becoming a musician."\nQuestion: What trait does Jack demonstrate?',
          'options': ['Determination','Selfishness','Arrogance','Laziness'],
          'correct_answer': 'Determination'},
         {'question': 'Passage: "The new policy was a double-edged sword—while it helped some people, it also created new problems."\nQuestion: What does “double-edged sword” mean?',
          'options': ['A dangerous weapon','A situation with both good and bad effects','A sharp object','A fair decision'],
          'correct_answer': 'A situation with both good and bad effects'},
         {'question': 'Passage: "The artist’s masterpiece was met with mixed reviews—some praised its uniqueness, while others found it too unconventional."\nQuestion: How was the artwork received?',
          'options': ['Opinions were divided','Everyone disliked it','Everyone liked it','No one noticed it'],
          'correct_answer': 'Opinions were divided'}
     ]},

    # Page 15: Instructions
    {'page_number': 15, 'title': 'Vocabulary Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Low difficulty</h4>
            <p>You will see a word and choose either its synonym (same meaning) or antonym (opposite meaning) from the multiple-choice options.</p>
            <p><em>Example:</em></p>
            <p>Word: "Soft".  Which word means the same as "Soft"? </p>
            <p>a) Hard</p>
            <p>b) Smooth</p>
            <p>c) Heavy</p>
            <p>d) Round</p>
            <p>Choose the correct answer from the multiple-choice options. There is <strong style="color: #d9534f;">only ONE correct answer</strong>:</p>
            <p><strong>b) Smooth</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 16: Multiple Choice Set 4 (UPDATED Word Questions)
    {'page_number': 16, 'title': 'Vocabulary Tasks - Low difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Word: "Happy"\nWhich word means the same as "Happy"?', 'options': ['Sad','Tired','Angry','Joyful'], 'correct_answer': 'Joyful'},
         {'question': 'Word: "Big"\nWhat is the opposite of "Big"?', 'options': ['Tiny','Large','Huge','Wide'], 'correct_answer': 'Tiny'},
         {'question': 'Word: "Easy"\nWhat is the opposite of "Easy"?', 'options': ['Warm','Soft','Simple','Difficult'], 'correct_answer': 'Difficult'},
         {'question': 'Word: "Cold"\nWhat is the opposite of "Cold"?', 'options': ['Freezing','Snowy','Hot','Cool'], 'correct_answer': 'Hot'},
         {'question': 'Word: "Fast"\nWhich word means the same as "Fast"?', 'options': ['Slow','Quick','Heavy','Hard'], 'correct_answer': 'Quick'}
     ]},

    # Page 17: Instructions
    {'page_number': 17, 'title': 'Vocabulary Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Medium difficulty</h4>
            <p>You will see a word used in a sentence and need to figure out its meaning based on the context.</p>
            <p><em>Example:</em></p>
            <p>"The manager’s instructions were vague, leaving the employees confused about what to do next." What does "vague" mean?</p>
            <p>a) Clear</p>
            <p>b) Unclear</p>
            <p>c) Exciting</p>
            <p>d) Strict</p>
            <p>Select the correct meaning from the multiple-choice options. There is only ONE correct answer:</p>
            <p><strong>b) Unclear</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 18: Multiple Choice Set 5 (UPDATED Sentence Questions)
    {'page_number': 18, 'title': 'Vocabulary Tasks - Medium difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Sentence: "The scientist made an astonishing discovery in the lab."\nQuestion: What does “astonishing” mean?',
          'options': ['Boring','Surprising','Unimportant','Unnoticed'],
          'correct_answer': 'Surprising'},
         {'question': 'Sentence: "The artist’s work was very intricate, filled with tiny details."\nQuestion: What does "intricate" mean?',
          'options': ['Simple','Large','Messy','Detailed'],
          'correct_answer': 'Detailed'},
         {'question': 'Sentence: "The teacher’s instructions were ambiguous, so the students were confused."\nQuestion: What does "ambiguous" mean?',
          'options': ['Clear','Helpful','Unclear','Short'],
          'correct_answer': 'Unclear'},
         {'question': 'Sentence: "The detective was meticulous in examining the evidence."\nQuestion: What does "meticulous" mean?',
          'options': ['Careful','Careless','Quick','Lazy'],
          'correct_answer': 'Careful'},
         {'question': 'Sentence: "The team’s victory was inevitable after they scored three goals."\nQuestion: What does "inevitable" mean?',
          'options': ['Uncertain','Avoidable','Unavoidable','Surprising'],
          'correct_answer': 'Unavoidable'}
     ]},

    # Page 19: Instructions
    {'page_number': 19, 'title': 'Vocabulary Tasks Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>High difficulty</h4>
            <p>You will see a complex or uncommon word in a sentence and must determine its meaning.</p>
            <p><em>Example:</em></p>
            <p>"The scientist's theory was considered spurious due to the lack of supporting evidence.." What does "spurious" mean?</p>
            <p>a) False</p>
            <p>b) Logical</p>
            <p>c) Popular</p>
            <p>d) Important</p>
            <p>Select the best definition from the options. There is only ONE correct answer:</p>
            <p><strong>a) False</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 20: Math Tasks Set 4 (UPDATED Word/Sentence Meaning)
    {'page_number': 20, 'title': 'Vocabulary Tasks - High difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': 'Word: "Lugubrious"\nWhat does "lugubrious" mean?', 'options': ['Cheerful','Mournful','Angry','Excited'], 'correct_answer': 'Mournful'},
         {'question': 'Word: "Ineffable"\nWhat does "ineffable" mean?', 'options': ['Impossible to express in words','Commonplace','Loud','Obvious'], 'correct_answer': 'Impossible to express in words'},
         {'question': 'Sentence: "The scientist’s hypothesis was tenuous, lacking solid evidence."\nQuestion: What does "tenuous" mean?',
          'options': ['Interesting','Strong','Well-supported','Weak'], 'correct_answer': 'Weak'},
         {'question': 'Sentence: "Her perfunctory response showed that she wasn’t truly interested."\nQuestion: What does "perfunctory" mean?',
          'options': ['Enthusiastic','Superficial','Thoughtful','Slow'], 'correct_answer': 'Superficial'},
         {'question': 'Sentence: "The CEO’s magnanimous gesture of donating his salary to charity was widely praised."\nQuestion: What does "magnanimous" mean?',
          'options': ['Generous','Selfish','Thoughtless','Secretive'], 'correct_answer': 'Generous'}
     ]},

    # Page 21: Instructions
    {'page_number': 21, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 22: Letter Grid Task
    {'page_number': 22, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 23: Demographics (Objective SES)
   {'page_number': 23,
    'title': 'Socioeconomic Background',
    'type': 'demographics',
    'tasks': [
        {'question': '1. How old are you?', 'type': 'text', 'name': 'age', 'required': True},
        {'question': '2. What gender do you identify with?', 'type': 'radio', 'name': 'gender',
         'options': ['Male', 'Female', 'Other'], 'required': True},
        {'question': '3. Do you have any parental figures?', 'type': 'radio', 'name': 'has_parent',
         'options': ['Yes', 'No'], 'required': True},
        {'question': '4. How many parental figures do you have?', 'type': 'radio', 'name': 'num_parents',
         'options': ['1', '2'], 'required': True, 'show_if': {'has_parent': 'Yes'}},

        # For 1 parent
        {'question': '5. Who is this person to you?', 'type': 'select', 'name': 'parent1_relation',
         'options': ['Biological mother', 'Biological father', 'Adoptive mother', 'Adoptive father',
                     'Legal guardian', 'Another Caregiver'], 'required': True,
         'show_if': {'num_parents': '1'}},

        {'question': '6. What is the highest level of education completed by this parental figure? (Primary parental figure refers to the person who had the most significant role in raising you, whether they are your biological parent, adoptive parent, legal guardian, or another caregiver (e.g., a grandparent or older sibling who provided for you))',
         'type': 'select', 'name': 'parent1_education',
         'options': ['No education', 'Primary School', 'Secondary School', 'High School',
                     'Vocational or technical training', 'Unfinished University / College degree',
                     'Bachelor’s Degree', 'Master’s degree', 'PhD degree'],
         'required': True, 'show_if': {'num_parents': '1'}},

        {'question': "7. What is this parental figure’s current employment status?",
         'type': 'select', 'name': 'parent1_employment',
         'options': ['Currently employed (full-time)', 'Currently employed (part-time)',
                     'Self-employed (owns a business, freelancer, independent worker, etc.)',
                     'Retired', 'Unemployed – Looking for work',
                     'Inactive – Not looking for work', 'Never worked'],
         'required': True, 'show_if': {'num_parents': '1'}},

        {'question': "8. What is your this parental figure’s current occupation (or last occupation if retired  / unemployed? (Based on the International Standard Classification of Occupations - ISCO-08)",
         'type': 'select', 'name': 'parent1_occupation',
         'options': ['Managers (e.g., company director, department head, senior government official, school principal)',
                     'Professionals (e.g., doctor, lawyer, engineer, university professor, scientist, economist, psychologist))',
                     'Technicians and Associate Professionals (e.g., laboratory technician, nursing assistant, IT support specialist, police officer, social worker, junior accountant)',
                     'Clerical Support Workers (e.g., office clerk, bank teller, administrative assistant, customer service representative)',
                     'Service and Sales Workers (e.g., salesperson, waiter, hairdresser, security guard, flight attendant, childcare worker)',
                     'Skilled Agricultural, Forestry, and Fishery Workers (e.g., farmer, fisher, forester, vineyard worker)',
                     'Craft and Related Trades Workers (e.g., carpenter, electrician, mechanic, baker, tailor, welder, construction worker)',
                     'Plant and Machine Operators and Assemblers (e.g., truck driver, factory worker, train operator, assembly line worker)',
                     'Elementary Occupations (e.g., cleaner, laborer, delivery person, garbage collector, housekeeper, street vendor)',
                     'Armed Forces Occupations (e.g., military personnel, soldier, naval officer, air force pilot)',
                     'Never worked'],
         'required': True, 'show_if': {'num_parents': '1'}},

        # For 2 parents — first
        {'question': '5. Who is this first person to you?', 'type': 'select', 'name': 'parent1a_relation',
         'options': ['Biological mother', 'Biological father', 'Adoptive mother', 'Adoptive father',
                     'Legal guardian', 'Another Caregiver'], 'required': True,
         'show_if': {'num_parents': '2'}},

        {'question': '6. What is the highest level of education completed by this first parental figure? (Primary parental figure refers to the person who had the most significant role in raising you, whether they are your biological parent, adoptive parent, legal guardian, or another caregiver (e.g., a grandparent or older sibling who provided for you))',
         'type': 'select', 'name': 'parent1a_education',
         'options': ['No education', 'Primary School', 'Secondary School', 'High School',
                     'Vocational or technical training', 'Unfinished University / College degree',
                     'Bachelor’s Degree', 'Master’s degree', 'PhD degree'],
         'required': True, 'show_if': {'num_parents': '2'}},

        {'question': "7. What is this first parental figure’s current employment status?",
         'type': 'select', 'name': 'parent1a_employment',
         'options': ['Currently employed (full-time)', 'Currently employed (part-time)',
                     'Self-employed (owns a business, freelancer, independent worker, etc.)',
                     'Retired', 'Unemployed – Looking for work',
                     'Inactive – Not looking for work', 'Never worked'],
         'required': True, 'show_if': {'num_parents': '2'}},

        {'question': "8. What is your this first parental figure’s current occupation (or last occupation if retired  / unemployed? (Based on the International Standard Classification of Occupations - ISCO-08)",
         'type': 'select', 'name': 'parent1a_occupation',
         'options': ['Managers (e.g., company director, department head, senior government official, school principal)',
                     'Professionals (e.g., doctor, lawyer, engineer, university professor, scientist, economist, psychologist))',
                     'Technicians and Associate Professionals (e.g., laboratory technician, nursing assistant, IT support specialist, police officer, social worker, junior accountant)',
                     'Clerical Support Workers (e.g., office clerk, bank teller, administrative assistant, customer service representative)',
                     'Service and Sales Workers (e.g., salesperson, waiter, hairdresser, security guard, flight attendant, childcare worker)',
                     'Skilled Agricultural, Forestry, and Fishery Workers (e.g., farmer, fisher, forester, vineyard worker)',
                     'Craft and Related Trades Workers (e.g., carpenter, electrician, mechanic, baker, tailor, welder, construction worker)',
                     'Plant and Machine Operators and Assemblers (e.g., truck driver, factory worker, train operator, assembly line worker)',
                     'Elementary Occupations (e.g., cleaner, laborer, delivery person, garbage collector, housekeeper, street vendor)',
                     'Armed Forces Occupations (e.g., military personnel, soldier, naval officer, air force pilot)',
                     'Never worked'],
         'required': True, 'show_if': {'num_parents': '2'}},

        # Second parental figure
        {'question': '9. Who is this second person to you?', 'type': 'select', 'name': 'parent2_relation',
         'options': ['Biological mother', 'Biological father', 'Adoptive mother', 'Adoptive father',
                     'Legal guardian', 'Another Caregiver'], 'required': True,
         'show_if': {'num_parents': '2'}},

        {'question': '10. What is the highest level of education completed by this second parental figure? (Primary parental figure refers to the person who had the most significant role in raising you, whether they are your biological parent, adoptive parent, legal guardian, or another caregiver (e.g., a grandparent or older sibling who provided for you))',
         'type': 'select', 'name': 'parent2_education',
         'options': ['No education', 'Primary School', 'Secondary School', 'High School',
                     'Vocational or technical training', 'Unfinished University / College degree',
                     'Bachelor’s Degree', 'Master’s degree', 'PhD degree'],
         'required': True, 'show_if': {'num_parents': '2'}},

        {'question': "11. What is this second parental figure’s current employment status?",
         'type': 'select', 'name': 'parent2_employment',
         'options': ['Currently employed (full-time)', 'Currently employed (part-time)',
                     'Self-employed (owns a business, freelancer, independent worker, etc.)',
                     'Retired', 'Unemployed – Looking for work',
                     'Inactive – Not looking for work', 'Never worked'],
         'required': True, 'show_if': {'num_parents': '2'}},

        {'question': "12. What is your this second parental figure’s current occupation (or last occupation if retired  / unemployed? (Based on the International Standard Classification of Occupations - ISCO-08)",
         'type': 'select', 'name': 'parent2_occupation',
         'options': ['Managers (e.g., company director, department head, senior government official, school principal)',
                     'Professionals (e.g., doctor, lawyer, engineer, university professor, scientist, economist, psychologist))',
                     'Technicians and Associate Professionals (e.g., laboratory technician, nursing assistant, IT support specialist, police officer, social worker, junior accountant)',
                     'Clerical Support Workers (e.g., office clerk, bank teller, administrative assistant, customer service representative)',
                     'Service and Sales Workers (e.g., salesperson, waiter, hairdresser, security guard, flight attendant, childcare worker)',
                     'Skilled Agricultural, Forestry, and Fishery Workers (e.g., farmer, fisher, forester, vineyard worker)',
                     'Craft and Related Trades Workers (e.g., carpenter, electrician, mechanic, baker, tailor, welder, construction worker)',
                     'Plant and Machine Operators and Assemblers (e.g., truck driver, factory worker, train operator, assembly line worker)',
                     'Elementary Occupations (e.g., cleaner, laborer, delivery person, garbage collector, housekeeper, street vendor)',
                     'Armed Forces Occupations (e.g., military personnel, soldier, naval officer, air force pilot)',
                     'Never worked', 'I did not have a parental figure'],
         'required': True, 'show_if': {'num_parents': '2'}},
    ]
},



    # Page 24: Self-Report (SES) (no feedback)
        # Page 24: Subjective SES Ladder
    {'page_number': 24, 'title': 'How You See Your Social Position',
     'content': '''
        <div style="text-align: left; line-height: 1.8; font-size: 1.1em;">
            <p>Think of this ladder as showing where people stand in your neighbourhood.</p>
            <p>By your neighbourhood, We mean within about a mile or 20 minutes walk of your home.</p>
            <p>At the top of the ladder are people who are best off - those who have the most money, the best education, and the most respected jobs.</p>
            <p>At the bottom of the ladder are the people who are the worst off - who have the least money, least education and the least respected jobs or no job.</p>
            <p>The higher up you are on this ladder, the closer you are to the people at the top; the lower you are, the closer you are to the bottom.</p>
            <p>Please click on the rung that best represents where you think you stand on the ladder.</p>
        </div>
        ''',
     'type': 'ladder'},


    # Page 25: Instructions
    {'page_number': 25, 'title': 'Timed Challenge', 'content': '''<div class="left-aligned-text">
        <p><strong>Get ready — this section is all about speed and accuracy.</strong></p>

        <p>You’ll complete a series of short tasks at different difficulty levels. Each one is timed.</p>

        <p>The timer will start counting down as soon as a task appears.</p>

        <p>As you go forward, the time for each task will get shorter.</p>

        <p>If you finish early, you can click <strong>Next</strong> to move on.</p>

        <p>If time runs out, the experiment will automatically move to the next task — even if you haven’t answered.</p>

        <p>When the difficulty level changes, the timer will reset completely.</p>

        <p><strong>Tip:</strong> Stay focused, think fast, and try to get as many correct answers as possible before time runs out.</p>

        <p><em>Good luck!</em></p>
    </div>''',
    'type': 'info'},

    # Page 26: Conditional Instructions (based on performance on page 4)
    {'page_number': 26, 'title': 'Math Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Low difficulty</h4>
            <p>ou will see a simple arithmetic problem (addition or subtraction). Solve the problem mentally and type your answer into the response box.</p>
            <p><em>Example:</em></p>
            <p>8 - 5 = ?</p>
            <p>In the line below, type your answer:</p>
            <p><strong>3</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 27: Continuous Scale Question (UPDATED continuous slider)
    {'page_number': 27, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},

    # Page 28: Math Tasks Set 5 (Timed, 15 tasks)
    {'page_number': 28, 'title': 'Math Challenge - Low difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': '5 + 3 = ?', 'correct_answer': '8'},
         {'question': '9 - 4 = ?', 'correct_answer': '5'},
         {'question': '7 + 2 = ?', 'correct_answer': '9'},
         {'question': '6 - 1 = ?', 'correct_answer': '5'},
         {'question': '8 - 3 = ?', 'correct_answer': '5'},
         {'question': '2 + 6 = ?', 'correct_answer': '8'},
         {'question': '9 - 7 = ?', 'correct_answer': '2'},
         {'question': '1 + 4 = ?', 'correct_answer': '5'},
         {'question': '7 - 5 = ?', 'correct_answer': '2'},
         {'question': '3 + 8 = ?', 'correct_answer': '11'},
         {'question': '6 - 2 = ?', 'correct_answer': '4'},
         {'question': '5 + 4 = ?', 'correct_answer': '9'},
         {'question': '9 - 6 = ?', 'correct_answer': '3'},
         {'question': '9 - 3 = ?', 'correct_answer': '6'},
         {'question': '2 + 5 = ?', 'correct_answer': '7'}
     ]},

    # Page 29: Continuous Scale (UPDATED continuous slider)
    {'page_number': 29, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 30: Instructions
    {'page_number': 30, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},
    # Page 31: Letter Grid Task
    {'page_number': 31, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 32: Conditional Instructions (based on performance on page 6)
    {'page_number': 32, 'title': 'Math Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Medium difficulty</h4>
            <p>You will see a two-step operation (addition, subtraction, multiplication, or division). Solve the problem mentally and type your answer into the response box.</p>
            <p><em>Example:</em></p>
            <p>38 + 30 − 11 = ?</p>
            <p>In the line below, type your answer:</p>
            <p><strong>57</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 33: Continuous Scale (UPDATED continuous slider)
    {'page_number': 33, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},

    # Page 34: Math Tasks Set 6 (Timed, 15 tasks)
    {'page_number': 34, 'title': 'Math Challenge - Medium Difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': '12 + 45 - 8 = ?', 'correct_answer': '49'},
         {'question': '36 ÷ 4 + 5 = ?', 'correct_answer': '14'},
         {'question': '(25 - 10) × 2 = ?', 'correct_answer': '30'},
         {'question': '100 - (30 + 20) = ?', 'correct_answer': '50'},
         {'question': '(15 × 2) - (8 ÷ 2) = ?', 'correct_answer': '26'},
         {'question': '50 + 25 - 12 = ?', 'correct_answer': '63'},
         {'question': '(80 ÷ 4) + 7 = ?', 'correct_answer': '27'},
         {'question': '34 - 18 + 9 = ?', 'correct_answer': '25'},
         {'question': '(40 × 2) - 50 = ?', 'correct_answer': '30'},
         {'question': '65 - (20 + 15) = ?', 'correct_answer': '30'},
         {'question': '(24 ÷ 6) + 13 = ?', 'correct_answer': '17'},
         {'question': '75 + 10 - 35 = ?', 'correct_answer': '50'},
         {'question': '(9 × 5) - 18 = ?', 'correct_answer': '27'},
         {'question': '(120 ÷ 10) + 15 = ?', 'correct_answer': '27'},
         {'question': '(48 ÷ 3) + 20 = ?', 'correct_answer': '36'}
     ]},

    # Page 35: Continuous Scale (UPDATED continuous slider)
    {'page_number': 35, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 36: Instructions
    {'page_number': 36, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 37: Letter Grid Task
    {'page_number': 37, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 38: Conditional Instructions (based on performance on page 8)
    {'page_number': 38, 'title': 'Math Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>High difficulty</h4>
            <p>You will see an equation where you must solve for x. Follow the steps to isolate x and find the correct answer.</p>
            <p><em>Example:</em></p>
            <p>Solve for x: 10x -13 = 37</p>
            <p>In the line below, type your answer:</p>
            <p><strong>5</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},
    # Page 39: Continuous Scale (UPDATED continuous slider)
    {'page_number': 39, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},

    # Page 40: Math Tasks Set 7 (Timed, 15 tasks)
    {'page_number': 40, 'title': 'Math Challenge - High difficulty', 'content': '', 'type': 'math',
     'tasks': [
         {'question': 'Solve for x: 3x + 5 = 14', 'correct_answer': '3'},
         {'question': 'Solve for x: 2(x - 4) = 10', 'correct_answer': '9'},
         {'question': 'Solve for x: 5x - 3 = 2x + 9', 'correct_answer': '4'},
         {'question': 'Solve for x: 4(x + 2) = 3x + 10', 'correct_answer': '2'},
         {'question': 'Solve for x: (x ÷ 2) + 7 = 12', 'correct_answer': '10'},
         {'question': 'Solve for x: 6x - 4 = 14', 'correct_answer': '3'},
         {'question': 'Solve for x: 7x + 3 = 24', 'correct_answer': '3'},
         {'question': 'Solve for x: (x ÷ 3) + 5 = 9', 'correct_answer': '12'},
         {'question': 'Solve for x: 2x + 9 = 3x - 5', 'correct_answer': '14'},
         {'question': 'Solve for x: (5x - 2) = (3x + 8)', 'correct_answer': '5'},
         {'question': 'Solve for x: (4x ÷ 2) + 6 = 10', 'correct_answer': '2'},
         {'question': 'Solve for x: (x - 3) × 2 = 12', 'correct_answer': '9'},
         {'question': 'Solve for x: (3x + 7) = (2x + 12)', 'correct_answer': '5'},
         {'question': 'Solve for x: 8x - 5 = 3x + 20', 'correct_answer': '5'},
         {'question': 'Solve for x: (2x ÷ 4) + 10 = 13', 'correct_answer': '6'}
     ]},

    # Page 41: Continuous Scale (UPDATED continuous slider)
    {'page_number': 41, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 42: Instructions
    {'page_number': 42, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 43: Letter Grid Task
    {'page_number': 43, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 44: Conditional Instructions (based on performance on page 10)
    {'page_number': 44, 'title': 'Reading Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Low difficulty</h4>
            <p>You will read a short sentence or passage, then answer a question about a fact that is directly stated in the text.</p>
            <p><em>Example:</em></p>
            <p>"The boy drank a glass of water." What did the boy drink?</p>
            <p>a) Milk</p>
            <p>b) Juice</p>
            <p>c) Water</p>
            <p>d) Soda</p>
            <p>Choose the correct answer from the multiple-choice options. There is only ONE correct answer:</p>
            <p><strong>c) Water</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 45: Continuous Scale (UPDATED continuous slider)
    {'page_number': 45, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},


    # Page 46: Multiple Choice Set 5 (Timed, 15 tasks)
    {'page_number': 46, 'title': 'Reading Challenge - Low difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'The dog is under the table. Where is the dog?', 'options': ['On the table','Under the table','Next to the door','In the garden'],'correct_answer': 'Under the table'},
         {'question': 'Tom drinks milk every morning. What does Tom drink?', 'options': ['Juice','Water','Milk','Coffee'],'correct_answer': 'Milk'},
         {'question': 'The sky is blue today. What color is the sky?', 'options': ['Blue','Green','Red','Yellow'],'correct_answer': 'Blue'},
         {'question': 'Sarah eats apples. What does Sarah eat?', 'options': ['Oranges','Bananas','Apples','Grapes'],'correct_answer': 'Apples'},
         {'question': 'It is raining outside. What is the weather like?', 'options': ['Sunny','Windy','Raining','Snowing'],'correct_answer': 'Raining'},
         {'question': "Emma’s cat is black. What color is the cat?", 'options': ['White','Gray','Brown','Black'],'correct_answer': 'Black'},
         {'question': 'John runs to school every day. How does John go to school?', 'options': ['By car','By bicycle','He runs','By bus'],'correct_answer': 'He runs'},
         {'question': 'The book is on the shelf. Where is the book?', 'options': ['On the table','On the shelf','In the bag','Under the chair'],'correct_answer': 'On the shelf'},
         {'question': "Lena’s dress is red. What color is Lena’s dress?", 'options': ['Blue','Red','Green','Yellow'],'correct_answer': 'Red'},
         {'question': 'Sam drinks water when he is thirsty. What does Sam drink?', 'options': ['Water','Coffee','Juice','Soda'],'correct_answer': 'Water'},
         {'question': 'The bus arrives at 8 AM. When does the bus arrive?', 'options': ['7 AM','9 AM','8 AM','10 AM'],'correct_answer': '8 AM'},
         {'question': 'Ben has two brothers. How many brothers does Ben have?', 'options': ['One','Three','Four','Two'],'correct_answer': 'Two'},
         {'question': 'The flowers in the garden are yellow. What color are the flowers?', 'options': ['Red','Blue','Yellow','Purple'],'correct_answer': 'Yellow'},
         {'question': 'Alice plays with her doll in the afternoon. When does Alice play?', 'options': ['In the afternoon','At night','In the morning','In the evening'],'correct_answer': 'In the afternoon'},
         {'question': 'The sun is shining brightly. What is the sun doing?', 'options': ['Raining','Shining','Sleeping','Melting'],'correct_answer': 'Shining'}
     ]},

    # Page 47: Continuous Scale (UPDATED continuous slider)
    {'page_number': 47, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 48: Instructions
    {'page_number': 48, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 49: Letter Grid Task
    {'page_number': 49, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 50: Conditional Instructions (based on performance on page 12)
    {'page_number': 50, 'title': 'Reading Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Medium difficulty</h4>
            <p>You will read a short passage and answer a question that requires you to infer meaning. The answer won’t be stated directly, but you can figure it out based on the text.</p>
            <p><em>Example:</em></p>
            <p>"David turned off the alarm, stretched, and headed to the kitchen to make coffee." What time of day is it likely?</p>
            <p>a) Morning</p>
            <p>b) Afternoon</p>
            <p>c) Evening</p>
            <p>d) Midnight</p>
            <p>Select the most appropriate answer:</p>
            <p><strong>a) Morning</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},
    # Page 51: Continuous Scale (UPDATED continuous slider)
    {'page_number': 51, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},

    # Page 52: Multiple Choice Set 6 (Timed, 15 tasks)
    {
    'page_number': 52,
    'title': 'Reading Challenge - Medium difficulty',
    'content': '',
    'type': 'mc',
    'tasks': [
        {
            'question': 'John forgot his umbrella, so he got wet. Why did John get wet?',
            'options': ['He took a shower', 'He was running', 'It was raining', 'He spilled water'],
            'correct_answer': 'It was raining'
        },
        {
            'question': 'Sarah studied all night but still felt nervous. How does Sarah feel?',
            'options': ['Excited', 'Nervous', 'Confident', 'Bored'],
            'correct_answer': 'Nervous'
        },
        {
            'question': 'Tom put on his coat and scarf before leaving. What is the weather like?',
            'options': ['Hot', 'Warm', 'Cold', 'Humid'],
            'correct_answer': 'Cold'
        },
        {
            'question': 'Mark looked for his phone under the couch. Where might his phone be?',
            'options': ['On the couch', 'Outside', 'In his bag', 'Under the couch'],
            'correct_answer': 'Under the couch'
        },
        {
            'question': 'Emma was late for school because she missed the bus. Why was Emma late?',
            'options': ['She overslept', 'She got lost', 'She missed the bus', 'She forgot her homework'],
            'correct_answer': 'She missed the bus'
        },
        {
            'question': 'Ben finished his homework before playing outside. What did Ben do first?',
            'options': ['He played outside', 'He did his homework', 'He ate dinner', 'He watched TV'],
            'correct_answer': 'He did his homework'
        },
        {
            'question': 'Even though she was scared, Anna entered the dark room. How did Anna feel?',
            'options': ['Brave', 'Nervous', 'Happy', 'Angry'],
            'correct_answer': 'Brave'
        },
        {
            'question': 'Ella’s stomach was growling, and she looked at the clock. What is she likely feeling?',
            'options': ['Sleepy', 'Angry', 'Hungry', 'Cold'],
            'correct_answer': 'Hungry'
        },
        {
            'question': 'Mike was shivering as he stepped outside. What can we infer?',
            'options': ['It is cold', 'It is raining', 'It is sunny', 'It is hot'],
            'correct_answer': 'It is cold'
        },
        {
            'question': 'Lisa checked her alarm clock and quickly got out of bed. What might she be worried about?',
            'options': ['Watching TV', 'Eating breakfast', 'Going to sleep', 'Being late'],
            'correct_answer': 'Being late'
        },
        {
            'question': 'Tom packed his suitcase and checked his passport. Where might he be going?',
            'options': ['To a party', 'On vacation', 'To work', 'To the gym'],
            'correct_answer': 'On vacation'
        },
        {
            'question': "Lily turned off the lights and got into bed. What is she likely doing?",
            'options': ['Going outside', 'Reading a book', 'Cleaning her room', 'Getting ready to sleep'],
            'correct_answer': 'Getting ready to sleep'
        },
        {
            'question': 'Lena set the table with plates and glasses. What is she preparing for?',
            'options': ['A picnic', 'A dinner party', 'A meeting', 'A workout session'],
            'correct_answer': 'A dinner party'
        },
        {
            'question': 'After watching a scary movie, Jake turned on all the lights. How does Jake feel?',
            'options': ['Excited', 'Sleepy', 'Scared', 'Confused'],
            'correct_answer': 'Scared'
        },
        {
            'question': 'Sophie’s eyes filled with tears as she read the letter. How is Sophie feeling?',
            'options': ['Happy', 'Surprised', 'Sad', 'Angry'],
            'correct_answer': 'Sad'
        }
    ]
}
,

    # Page 53: Continuous Scale (UPDATED continuous slider)
    {'page_number': 53, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 54: Instructions
    {'page_number': 54, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 55: Letter Grid Task
    {'page_number': 55, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 56: Conditional Instructions (based on performance on page 14)
    {'page_number': 56, 'title': 'Reading Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>High difficulty</h4>
            <p>You will read a more complex passage and answer a question that requires deeper thinking. This may involve understanding the author’s tone, interpreting abstract ideas, or identifying their intent.</p>
            <p><em>Example:</em></p>
            <p>"The room fell silent as Nora entered, her reputation preceding her." What does this imply about Nora?</p>
            <p>a) She is well-known</p>
            <p>b) She is quiet</p>
            <p>c) She is invisible</p>
            <p>d) She is new to the group</p>
            <p>Select the most appropriate answer:</p>
            <p><strong>a) She is well-known</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 57: Continuous Scale (UPDATED continuous slider)
    {'page_number': 57, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},


    # Page 58: Multiple Choice Set 7 (Timed, 15 tasks)
    {'page_number': 58, 'title': 'Reading Challenge - High Difficulty', 'content': '', 'type': 'mc',
     'tasks': [
        {
            'question': 'Despite his wealth, James longed for a simpler life. What does this suggest?',
            'options': ['He wants more money', 'He values simplicity over wealth', 'He dislikes his childhood', 'He is greedy'],
            'correct_answer': 'He values simplicity over wealth'
        },
        {
            'question': 'The new technology had unforeseen consequences. What does this imply?',
            'options': ['The effects were unexpected', 'The results were planned', 'The technology failed', 'The innovation was useful'],
            'correct_answer': 'The effects were unexpected'
        },
        {
            'question': 'The teacher praised Liam for his insightful comment. What does “insightful” mean?',
            'options': ['Silly', 'Confusing', 'Thoughtful and intelligent', 'Off-topic'],
            'correct_answer': 'Thoughtful and intelligent'
        },
        {
            'question': 'Despite her initial hesitation, Maria embraced the challenge. What does this suggest?',
            'options': ['She refused to participate', 'She overcame her fears', 'She gave up quickly', 'She was uninterested'],
            'correct_answer': 'She overcame her fears'
        },
        {
            'question': 'Even though Henry disliked public speaking, he took the stage with aplomb. What does this tell us?',
            'options': ['He was nervous', 'He handled it with confidence', 'He refused to speak', 'He asked someone else to speak'],
            'correct_answer': 'He handled it with confidence'
        },
        {
            'question': 'Clara’s confidence grew as she continued her speech. What is the main idea?',
            'options': ['Clara was nervous', 'Clara became more confident', 'Clara forgot her speech', 'Clara was uninterested'],
            'correct_answer': 'Clara became more confident'
        },
        {
            'question': 'The scientist’s theory was met with skepticism. How was it received?',
            'options': ['With trust', 'With doubt', 'With excitement', 'With celebration'],
            'correct_answer': 'With doubt'
        },
        {
            'question': "The experiment's results were inconclusive. What does this mean?",
            'options': ['The results were unclear', 'The results were proven', 'The experiment failed', 'The results were ignored'],
            'correct_answer': 'The results were unclear'
        },
        {
            'question': 'Despite the controversy, the artist remained steadfast in her vision. What does "steadfast" mean?',
            'options': ['Unwavering', 'Uncertain', 'Weak', 'Confused'],
            'correct_answer': 'Unwavering'
        },
        {
            'question': 'The author uses sarcasm to criticize the government. What literary device is used?',
            'options': ['Irony', 'Hyperbole', 'Metaphor', 'Allusion'],
            'correct_answer': 'Irony'
        },
        {
            'question': 'The novel’s ambiguous ending left readers puzzled. How does the story end?',
            'options': ['With a clear resolution', 'With a cliffhanger', 'With multiple possible interpretations', 'With an abrupt conclusion'],
            'correct_answer': 'With multiple possible interpretations'
        },
        {
            'question': 'The speaker’s words resonated deeply with the audience. What does this mean?',
            'options': ['The audience felt confused by the words', 'The audience found the words uninteresting', 'The audience strongly connected with the words', 'The audience disagreed with the words'],
            'correct_answer': 'The audience strongly connected with the words'
        },
        {
            'question': 'The team’s perseverance despite the challenges was commendable. What does this tell us?',
            'options': ['The team overcame their challenges easily', 'The team faced many challenges without giving up', 'The team was disorganized and unprepared', 'The team struggled and eventually gave up'],
            'correct_answer': 'The team faced many challenges without giving up'
        },
        {
            'question': 'The manager commended Jordan for his diligence. What does “commended” mean?',
            'options': ['Ignored', 'Criticized', 'Praised', 'Warned'],
            'correct_answer': 'Praised'
        },
        {
            'question': 'The character’s transformation was a testament to personal growth. What does this mean?',
            'options': ['The character failed to change throughout the story', 'The character underwent a significant positive change', 'The character remained stagnant and unchanged', "The character's growth was a failure"],
            'correct_answer': 'The character underwent a significant positive change'
        }
    ]},

    # Page 59: Continuous Scale (UPDATED continuous slider)
    {'page_number': 59, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 60: Instructions
    {'page_number': 60, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 61: Letter Grid Task
    {'page_number': 61, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 62: Conditional Instructions (based on performance on page 16)
    {'page_number': 62, 'title': 'Vocabulary Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Low difficulty</h4>
            <p>You will see a word and choose either its synonym (same meaning) or antonym (opposite meaning) from the multiple-choice options.</p>
            <p><em>Example:</em></p>
            <p>Word: "Soft".  Which word means the same as "Soft"? </p>
            <p>a) Hard</p>
            <p>b) Smooth</p>
            <p>c) Heavy</p>
            <p>d) Round</p>
            <p>Choose the correct answer from the multiple-choice options. There is only ONE correct answer:</p>
            <p><strong>b) Smooth</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 63: Continuous Scale (UPDATED continuous slider)
    {'page_number': 63, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},


    # Page 64: Multiple Choice Set 8 (Timed, 15 tasks)
    {'page_number': 64, 'title': 'Vocabulary Challenge - Low difficulty', 'content': '', 'type': 'mc',
     'tasks': [
        {
            'question': 'Word: Fast\nQuestion: What is the opposite of "Fast"?',
            'options': ['Slow', 'Quick', 'Heavy', 'Hard'],
            'correct_answer': 'Slow'
        },
        {
            'question': 'Word: Bright\nQuestion: What is the opposite of "Bright"?',
            'options': ['Dark', 'Happy', 'Heavy', 'Large'],
            'correct_answer': 'Dark'
        },
        {
            'question': 'Word: Laugh\nQuestion: Which word means the same as "Laugh"?',
            'options': ['Cry', 'Giggle', 'Sleep', 'Shout'],
            'correct_answer': 'Giggle'
        },
        {
            'question': 'Word: Kind\nQuestion: What is the opposite of "Kind"?',
            'options': ['Nice', 'Rude', 'Generous', 'Thoughtful'],
            'correct_answer': 'Rude'
        },
        {
            'question': 'Word: Weak\nQuestion: What is the opposite of "Weak"?',
            'options': ['Small', 'Tiny', 'Strong', 'Soft'],
            'correct_answer': 'Strong'
        },
        {
            'question': 'Word: Shy\nQuestion: Which word means the same as "Shy"?',
            'options': ['Timid', 'Brave', 'Happy', 'Fast'],
            'correct_answer': 'Timid'
        },
        {
            'question': 'Word: Hot\nQuestion: What is the opposite of "Hot"?',
            'options': ['Warm', 'Cold', 'Dry', 'Light'],
            'correct_answer': 'Cold'
        },
        {
            'question': 'Word: Soft\nQuestion: What is the opposite of "Soft"?',
            'options': ['Hard', 'Round', 'Light', 'Sharp'],
            'correct_answer': 'Hard'
        },
        {
            'question': 'Word: Big\nQuestion: Which word means the same as "Big"?',
            'options': ['Short', 'Tiny', 'Small', 'Huge'],
            'correct_answer': 'Huge'
        },
        {
            'question': 'Word: Tall\nQuestion: What is the opposite of "Tall"?',
            'options': ['Thin', 'Big', 'Wide', 'Short'],
            'correct_answer': 'Short'
        },
        {
            'question': 'Word: Sad\nQuestion: What is the opposite of "Sad"?',
            'options': ['Tired', 'Short', 'Strong', 'Dark'],
            'correct_answer': 'Happy'
        },
        {
            'question': 'Word: Easy\nQuestion: What is the opposite of "Easy"?',
            'options': ['Simple', 'Warm', 'Difficult', 'Soft'],
            'correct_answer': 'Difficult'
        },
        {
            'question': 'Word: Long\nQuestion: What is the opposite of "Long"?',
            'options': ['Heavy', 'Wide', 'Short', 'Bright'],
            'correct_answer': 'Short'
        },
        {
            'question': 'Word: Empty\nQuestion: What is the opposite of "Empty"?',
            'options': ['Dry', 'Open', 'Small', 'Full'],
            'correct_answer': 'Full'
        },
        {
            'question': 'Word: Quiet\nQuestion: What is the opposite of "Quiet"?',
            'options': ['Bright', 'Fast', 'Loud', 'Clear'],
            'correct_answer': 'Loud'
        }
    ]},

        # Page 65: Continuous Scale (UPDATED continuous slider)
    {'page_number': 65, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 66: Instructions
    {'page_number': 66, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 67: Letter Grid Task
    {'page_number': 67, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible.', 'type': 'letter_grid'},

    # Page 68: Conditional Instructions (based on performance on page 18)
    {'page_number': 68, 'title': 'Vocabulary Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>Medium difficulty</h4>
            <p>You will see a word used in a sentence and need to figure out its meaning based on the context.</p>
            <p><em>Example:</em></p>
            <p>"The manager’s instructions were vague, leaving the employees confused about what to do next." What does "vague" mean?</p>
            <p>a) Clear</p>
            <p>b) Unclear</p>
            <p>c) Exciting</p>
            <p>d) Strict</p>
            <p>Select the correct meaning from the multiple-choice options. There is only ONE correct answer:</p>
            <p><strong>b) Unclear</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 69: Continuous Scale (UPDATED continuous slider)
    {'page_number': 69, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},


    # Page 70: Math Tasks Set 8 (Timed, 15 tasks)
    {'page_number': 70, 'title': 'Vocabulary Challenge - Medium Difficulty', 'content': '', 'type': 'math',
     'tasks': [
     {'question': 'Sentence: The toddler was very clumsy and kept dropping his toys.\nQuestion: What does "clumsy" mean?', 
      'options': ['Careful', 'Awkward', 'Strong', 'Soft'], 'correct_answer': 'Awkward'},
     {'question': 'Sentence: After jogging for an hour, Sarah was exhausted.\nQuestion: What does "exhausted" mean?', 
      'options': ['Tired', 'Energetic', 'Excited', 'Bored'], 'correct_answer': 'Tired'},
     {'question': 'Sentence: The child was reluctant to try the new food.\nQuestion: What does "reluctant" mean?', 
      'options': ['Eager', 'Hesitant', 'Excited', 'Curious'], 'correct_answer': 'Hesitant'},
     {'question': 'Sentence: The class was eager to go on the field trip.\nQuestion: What does "eager" mean?', 
      'options': ['Nervous', 'Tired', 'Enthusiastic', 'Reluctant'], 'correct_answer': 'Enthusiastic'},
     {'question': 'Sentence: The instructions were very confusing, and nobody knew what to do.\nQuestion: What does "confusing" mean?', 
      'options': ['Hard to understand', 'Clear', 'Exciting', 'Fun'], 'correct_answer': 'Hard to understand'},
     {'question': 'Sentence: The snake moved in a stealthy way through the grass.\nQuestion: What does "stealthy" mean?', 
      'options': ['Quick', 'Playful', 'Noisy', 'Sneaky'], 'correct_answer': 'Sneaky'},
     {'question': 'Sentence: After the storm, the house was in a shambles.\nQuestion: What does "shambles" mean?', 
      'options': ['Small', 'Clean', 'Messy', 'Broken'], 'correct_answer': 'Messy'},
     {'question': 'Sentence: The scientist’s discovery was remarkable.\nQuestion: What does "remarkable" mean?', 
      'options': ['Impressive', 'Unimportant', 'Small', 'Fast'], 'correct_answer': 'Impressive'},
     {'question': 'Sentence: The baby was fascinated by the moving mobile above his crib.\nQuestion: What does "fascinated" mean?', 
      'options': ['Confused', 'Bored', 'Very interested', 'Angry'], 'correct_answer': 'Very interested'},
     {'question': 'Sentence: The team was triumphant after winning the championship.\nQuestion: What does "triumphant" mean?', 
      'options': ['Sad', 'Victorious', 'Nervous', 'Quiet'], 'correct_answer': 'Victorious'},
     {'question': 'Sentence: She had a soothing voice that made everyone feel calm.\nQuestion: What does "soothing" mean?', 
      'options': ['Harsh', 'Loud', 'Calming', 'Exciting'], 'correct_answer': 'Calming'},
     {'question': 'Sentence: The cake was delicious, and everyone wanted another slice.\nQuestion: What does "delicious" mean?', 
      'options': ['Spicy', 'Boring', 'Cold', 'Tasty'], 'correct_answer': 'Tasty'},
     {'question': 'Sentence: The volcano had been dormant for decades before erupting.\nQuestion: What does "dormant" mean?', 
      'options': ['Active', 'Inactive', 'Loud', 'Explosive'], 'correct_answer': 'Inactive'},
     {'question': 'Sentence: The children were giddy with excitement before the trip.\nQuestion: What does "giddy" mean?', 
      'options': ['Annoyed', 'Angry', 'Tired', 'Overly excited'], 'correct_answer': 'Overly excited'},
     {'question': 'Sentence: The hero’s bravery was legendary.\nQuestion: What does "legendary" mean?', 
      'options': ['Hard', 'Small', 'Famous', 'Unknown'], 'correct_answer': 'Famous'}
 ]},

    # Page 71: Continuous Scale (UPDATED continuous slider)
    {'page_number': 71, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 72: Instructions
    {'page_number': 72, 'title': 'Letter Grid Task Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <p>You'll see a grid of letters. A target letter will be shown at the top (e.g., \"Find all the T's\").</p> 
            <p>Click on the first target letter you spot.</p>
            <p>The grid will disappear when time runs out.</p>
            <p>Be quick and accurate. Only click the correct letter.</p> 
         </div> 

        <p style="margin-top: 20px;">

        </div>
        ''',
    'type': 'instructions'},

    # Page 73: Letter Grid Task
    {'page_number': 73, 'title': 'Letter Grid Task', 'content': 'Find the target letter as quickly as possible. When you click the target letter correctly, a new grid is generated.', 'type': 'letter_grid'},

    # Page 74: Conditional Instructions (based on performance on page 20)
    {'page_number': 74, 'title': 'Vocabulary Challenge Instructions', 'content': '''
        <div class="info-container">
        <div class="info-section">
            <h4>High difficulty</h4>
            <p>You will see a complex or uncommon word in a sentence and must determine its meaning.</p>
            <p><em>Example:</em></p>
            <p>"The scientist's theory was considered spurious due to the lack of supporting evidence.." What does "spurious" mean?</p>
            <p>a) False</p>
            <p>b) Logical</p>
            <p>c) Popular</p>
            <p>d) Important</p>
            <p>Select the best definition from the options. There is only ONE correct answer:</p>
            <p><strong>a) False</strong></p>
        </div>

        <p style="margin-top: 20px;">Click Next when you're ready to start.</p>

        </div>
        ''',
        'type': 'info'},

    # Page 75: Continuous Scale (UPDATED continuous slider)
    {'page_number': 75, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None}
     ]},


    # Page 76: Multiple Choice Set 9 (Timed, 15 tasks)
    {'page_number': 76, 'title': 'Vocabulary Challenge - High difficulty', 'content': '', 'type': 'mc',
     'tasks': [
         {'question': 'Sentence: Despite the overwhelming criticism, the author remained unperturbed and continued her work.\nQuestion: What does "unperturbed" mean?',
          'options': ['Angry', 'Confused', 'Unbothered', 'Anxious'], 'correct_answer': 'Unbothered'},
         {'question': 'Sentence: The scientist’s work was filled with nuances that only experts could fully appreciate.\nQuestion: What does "nuances" mean?',
          'options': ['Subtle distinctions', 'Mistakes', 'Complications', 'Inconsistencies'], 'correct_answer': 'Subtle distinctions'},
         {'question': 'Sentence: His acrimonious speech left the audience in shock.\nQuestion: What does "acrimonious" mean?',
          'options': ['Inspirational', 'Friendly', 'Joyful', 'Bitter'], 'correct_answer': 'Bitter'},
         {'question': 'Sentence: The senator’s response was so equivocal that no one understood his stance on the issue.\nQuestion: What does "equivocal" mean?',
          'options': ['Clear', 'Ambiguous', 'Honest', 'Concise'], 'correct_answer': 'Ambiguous'},
         {'question': 'Sentence: The new policy had deleterious effects on the environment.\nQuestion: What does "deleterious" mean?',
          'options': ['Temporary', 'Beneficial', 'Unnoticeable', 'Harmful'], 'correct_answer': 'Harmful'},
         {'question': 'Sentence: Her speech was taciturn, consisting of only a few short sentences.\nQuestion: What does "taciturn" mean?',
          'options': ['Overcomplicated', 'Passionate', 'Long-winded', 'Quiet'], 'correct_answer': 'Quiet'},
         {'question': 'Sentence: The king’s rule was marked by despotism, leaving no room for opposition.\nQuestion: What does "despotism" mean?',
          'options': ['Diplomacy', 'Tyranny', 'Generosity', 'Cowardice'], 'correct_answer': 'Tyranny'},
         {'question': 'Sentence: The soldier showed indomitable courage in battle.\nQuestion: What does "indomitable" mean?',
          'options': ['Reckless', 'Hesitant', 'Unconquerable', 'Insignificant'], 'correct_answer': 'Unconquerable'},
         {'question': 'Sentence: Her artwork was full of esoteric references that few could understand.\nQuestion: What does "esoteric" mean?',
          'options': ['Difficult to understand', 'Beautiful', 'Unnecessary', 'Famous'], 'correct_answer': 'Difficult to understand'},
         {'question': 'Sentence: His pedantic explanations frustrated his audience.\nQuestion: What does "pedantic" mean?',
          'options': ['Rushed', 'Engaging', 'Simplistic', 'Overly concerned with details'], 'correct_answer': 'Overly concerned with details'},
         {'question': 'Sentence: The philosopher’s argument was full of sophistry, designed to mislead rather than inform.\nQuestion: What does "sophistry" mean?',
          'options': ['Deceptive reasoning', 'Clear logic', 'Inspirational ideas', 'Ancient philosophy'], 'correct_answer': 'Deceptive reasoning'},
         {'question': 'Sentence: The novel’s plot was labyrinthine, with twists and turns that kept readers guessing.\nQuestion: What does "labyrinthine" mean?',
          'options': ['Dull', 'Predictable', 'Complicated', 'Short'], 'correct_answer': 'Complicated'},
         {'question': 'Sentence: Her capricious behavior made it hard to predict her reactions.\nQuestion: What does "capricious" mean?',
          'options': ['Cautious', 'Thoughtful', 'Reliable', 'Unpredictable'], 'correct_answer': 'Unpredictable'},
         {'question': 'Sentence: The lawyer presented an unassailable argument that no one could refute.\nQuestion: What does "unassailable" mean?',
          'options': ['Impossible to dispute', 'Easily criticized', 'Unethical', 'Unconvincing'], 'correct_answer': 'Impossible to dispute'},
         {'question': 'Sentence: Despite the tragedy, he maintained a sense of sanguine optimism.\nQuestion: What does "sanguine" mean?',
          'options': ['Devastated', 'Hopeful', 'Indifferent', 'Furious'], 'correct_answer': 'Hopeful'}
     ]},

    # Page 77: Continuous Scale (UPDATED continuous slider)
    {'page_number': 77, 'title': '', 'content': '', 'type': 'continuous',
     'tasks': [
         {'question': 'How stressed do you feel right now? (Can click anywhere on the line from 0 to 100).', 'correct_answer': None},
         {'question': 'To what extent do you think the ticking clock contributed to your stress?: Rate from 0–100', 'correct_answer': None}
     ]},

    # Page 80: Yes/No Questions
   {'page_number': 80, 'title': 'Final Questions', 'type': 'demographics',
 'tasks': [
     {'question': '1. Are you a native English speaker?', 'type': 'radio', 'name': 'native_english',
      'options': ['Yes', 'No'], 'required': True},

     {'question': '2. Do you have any math classes in your university program?', 'type': 'radio', 'name': 'math_classes',
      'options': ['Yes', 'No'], 'required': True},

     {'question': '3. What is the name of your university program (e.g., Psychology, Engineering)?',
      'type': 'text', 'name': 'university_program', 'required': True},

     {'question': '4. What is your current level of study? (e.g., Bachelor, Master 1, PhD)',
      'type': 'text', 'name': 'study_level', 'required': True}
 ]},

    # Page 81: End
    {'page_number': 81, 'title': 'End', 'content': '', 'type': 'end'}
]

###############################################################################
# Helper functions
###############################################################################
def get_page(page_number):
    for p in pages:
        if p['page_number'] == page_number:
            return p
    return None

def is_correct(user_ans, correct_ans):
    ua = user_ans.strip().lower()
    ca = correct_ans.strip().lower()
    if not ua or not ca:
        return ua == ca
    try:
        return float(ua) == float(ca)
    except ValueError:
        return ua == ca

###############################################################################
# Routes
###############################################################################
@app.route('/')
def index():
    session.clear()
    session['responses'] = {}
    session['start_times'] = {}
    session['current_page'] = 1
    session['pages_to_skip'] = []
    for pnum in [4,6,8,10,12,14,16,18,20,28,34,40,46,52,58,64,70,76]:
        session.pop(f'current_task_{pnum}', None)
    return redirect(url_for('page', page_num=1))

@app.route("/ping")
def ping():
    return "pong"


@app.route('/page/<int:page_num>', methods=['GET','POST'])
def page(page_num):
    page_data = get_page(page_num)

    # Show disclaimer message before fast-response pages
    disclaimer_pages = [4, 6, 8, 10, 12, 14, 16, 18, 20]
    if request.method == 'GET' and page_num in disclaimer_pages:
        if not session.get(f'seen_disclaimer_{page_num}'):
            session[f'seen_disclaimer_{page_num}'] = True
            return render_template('page.html',
                                    page={'type': 'disclaimer', 'content': '', 'title': 'Get Ready'},
                                    next_page=page_num,
                                    progress_percent=round((page_num / 81) * 100))



    # Dynamically skip pages marked to be skipped
    if page_num in session.get('pages_to_skip', []) or page_num in [78, 79]:
        return redirect(url_for('page', page_num=page_num + 1))

    if not page_data:
        return redirect(url_for('submit'))

    # Timer pages logic
    timed_pages = [28,34,40,46,52,58,64,70,76]
    time_pair_map = {
        28: 4, 34: 6, 40: 8, 46: 10, 52: 12,
        58: 14, 64: 16, 70: 18, 76: 20
    }
    time_limit = None
    if page_num in timed_pages:
        source_page = time_pair_map.get(page_num)
        avg_key = f'avg_time_page{source_page}'
        base = session.get(avg_key, 10.0) * 1.4
        key = f'current_task_{page_num}'
        current_index = session.get(key, 1)
        time_limit = base * (0.95 ** (current_index - 1))

    single_task_types = ['math','mc','continuous']
    feedback = None
    feedback_color = None
    current_task = None
    total_tasks = len(page_data.get('tasks', []))
    if page_data.get('tasks') and page_data['type'] in single_task_types:
        key = f'current_task_{page_num}'
        current_index = session.get(key, 1)
        if current_index <= total_tasks:
            current_task = page_data['tasks'][current_index - 1]

    if request.method == 'POST':
        if page_data['type'] == 'letter_grid':
            letter_count = clean(request.form.get('letter_count', '0'))
            responses = session.get('responses', {})
            responses[str(page_num)] = {'letter_count': letter_count}
            session['responses'] = responses
            autosave_responses(responses)  # ✅ <--- add this!
            return redirect(url_for('page', page_num=page_num+1))


        if page_data['type'] == 'ladder':
            ladder_choice = clean(request.form.get('ladder_choice', ''))
            responses = session.get('responses', {})
            responses[str(page_num)] = {'ladder_choice': ladder_choice}
            session['responses'] = responses
            return redirect(url_for('page', page_num=page_num+1))

        if page_data['type'] == 'yesno':
            responses = session.get('responses', {})
            data = {k: clean(v) for k, v in request.form.items()}
            responses[str(page_num)] = data
            session['responses'] = responses
            autosave_responses(responses)
            return redirect(url_for('page', page_num=page_num+1))

        if page_num in [23,24]:
            responses = session.get('responses', {})
            data = {k: clean(v) for k, v in request.form.items()}
            responses[str(page_num)] = data
            session['responses'] = responses
            autosave_responses(responses)
            return redirect(url_for('page', page_num=page_num+1))

        if page_data.get('tasks') and page_data['type'] in single_task_types:
            user_answer = clean(request.form.get('answer', ''))
            task_time = clean(request.form.get('task_time', '0'))
            if current_task and current_task.get('correct_answer'):
                if is_correct(user_answer, current_task['correct_answer']):
                    feedback = "Correct"
                    feedback_color = "green"
                else:
                    feedback = "Incorrect"
                    feedback_color = "red"
            responses = session.get('responses', {})
            if str(page_num) not in responses:
                responses[str(page_num)] = []
            responses[str(page_num)].append({
                'task_index': current_index,
                'answer': user_answer,
                'feedback': feedback,
                'task_time': task_time
            })
            session['responses'] = responses
            autosave_responses(responses)
            print(f"✅ Page {page_num} | Task {current_index} marked {feedback}")
            current_index += 1
            session[f'current_task_{page_num}'] = current_index

            # Save average time for pages 4,6,8,...,20
            if page_num in [4,6,8,10,12,14,16,18,20] and current_index > total_tasks:
                tasks_data = responses.get(str(page_num), [])
                total_time = 0.0
                count_time = 0
                for r in tasks_data:
                    try:
                        t = float(r.get('task_time', '0').strip())
                        total_time += t
                        count_time += 1
                    except ValueError:
                        pass
                if count_time > 0:
                    session[f'avg_time_page{page_num}'] = total_time / count_time

            if current_index > total_tasks:
                responses = session.get('responses', {})
                tasks_data = responses.get(str(page_num), [])

                # Count accuracy for possible skip logic
                correct_count = sum(1 for r in tasks_data if r.get('feedback') == "Correct")
                total = len(tasks_data)
                accuracy = (correct_count / total) * 100 if total > 0 else 0

                # Store average response time (used in timed tasks)
                if page_num in [4,6,8,10,12,14,16,18,20]:
                    try:
                        times = [float(r.get('task_time', 0)) for r in tasks_data if r.get('task_time')]
                        if times:
                            avg_time = sum(times) / len(times)
                            session[f'avg_time_page{page_num}'] = avg_time
                    except:
                        pass

                # Set up skip ranges for underperformance
                skip_mapping = {
                    4: list(range(26, 32)),
                    6: list(range(32, 38)),
                    8: list(range(38, 44)),
                    10: list(range(44, 50)),
                    12: list(range(50, 56)),
                    14: list(range(56, 62)),
                    16: list(range(62, 68)),
                    18: list(range(68, 74)),
                    20: list(range(74, 78)),
                }
                if page_num in skip_mapping and accuracy < 40:
                    session['pages_to_skip'].extend(skip_mapping[page_num])

                # Routing logic
                if page_num < 25:
                    next_page = page_num + 1
                    
                elif page_num == 25:
                    next_page = 26


                else:
                    next_page = page_num + 1

               # Skip unwanted pages AND enforce experiment flow
                skipped_pages = session.get('pages_to_skip', [])
                while True:
                    # Explicitly skip deleted pages 78 & 79 and any low-perf skip range
                    if (next_page in skipped_pages or next_page in [78, 79]) and next_page not in [80, 81]:
                        next_page += 1
                    else:
                        break


                session.pop(f'current_task_{page_num}', None)
                return redirect(url_for('page', page_num=next_page))

            else:
                current_task = page_data['tasks'][current_index - 1]
                progress_percent = round((page_num / 81) * 100)
                return render_template('page.html',
                                    page=page_data,
                                    current_task=current_task,
                                    task_number=current_index,
                                    total_tasks=total_tasks,
                                    feedback=feedback,
                                    feedback_color=feedback_color,
                                    time_limit=time_limit,
                                    manual_next=(page_data['type'] != 'continuous'),
                                    progress_percent=progress_percent)

        else:
            data = {k: clean(v) for k, v in request.form.items()}
            responses = session.get('responses', {})
            responses[str(page_num)] = data
            session['responses'] = responses
            autosave_responses(responses)
            return redirect(url_for('page', page_num=page_num+1))

    # GET
    grid = None
    target_letter = None
    if page_data['type'] == 'letter_grid':
        letters = string.ascii_uppercase
        grid = []
        for i in range(2):
            row = [random.choice(letters) for _ in range(15)]
            grid.append(row)
        target_letter = random.choice(letters)
        if not any(target_letter in row for row in grid):
            r = random.randint(0, len(grid)-1)
            c = random.randint(0, len(grid[0])-1)
            grid[r][c] = target_letter

    progress_percent = round((page_num / 81) * 100)

    return render_template('page.html',
                        page=page_data,
                        current_task=current_task,
                        task_number=session.get(f'current_task_{page_num}', 1),
                        total_tasks=total_tasks,
                        feedback=feedback,
                        feedback_color=feedback_color,
                        grid=grid,
                        target_letter=target_letter,
                        time_limit=time_limit,
                        progress_percent=progress_percent)

@app.route('/submit')
def submit():
    filename = None
    if session.get('responses'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder = 'autosaves'
        os.makedirs(folder, exist_ok=True)
        filename = f'finalsave_{timestamp}.csv'
        filepath = os.path.join(folder, filename)
        autosave_responses(session['responses'])
    return render_template('submit.html', filename=filename)

@app.route('/download/<filename>')
def download():
    responses = session.get('responses', [])
    if not responses:
        return "No data to download."

    # Save as CSV-like structure in memory
    output = io.StringIO()
    headers = set()
    for response in responses:
        headers.update(response.keys())
    headers = sorted(headers)
    output.write(",".join(headers) + "\n")
    for response in responses:
        row = [str(response.get(h, "")) for h in headers]
        output.write(",".join(row) + "\n")
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='responses.csv')


if __name__ == '__main__':
    app.run(debug=True) 