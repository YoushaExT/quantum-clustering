import ipywidgets as widgets
from IPython.display import display

class MCQQuiz:
    def __init__(self, title="Interactive Quiz"):
        """Initialize the quiz system with a title."""
        self.title = title
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.total = 0
        self.quiz_started = False
        
        # Apply global CSS styling
        self._inject_css()
        
        # Create main UI components
        self.title_widget = widgets.HTML(f"<h2>{self.title}</h2>")
        self.question_widget = widgets.HTML("")
        self.feedback_widget = widgets.HTML("")
        self.next_button = widgets.Button(description="Start Quiz")
        self.progress_widget = widgets.HTML("")
        
        # Event handlers
        self.next_button.on_click(self.next_question)
        
        # Main container
        self.main_container = widgets.VBox([
            self.title_widget,
            self.question_widget,
            self.feedback_widget,
            self.next_button,
            self.progress_widget
        ])
    
    def _inject_css(self):
        """Inject CSS styling for better radio button."""
        css = """
        <style>
        .widget-label-basic {
            overflow: visible !important;
        }
        .widget-radio-box {
            gap: 16px !important;
        }
        </style>
        """
        display(widgets.HTML(css))
    
    def add_single_choice_question(self, question, options, correct_answer, explanation=None):
        """Add a single-choice question to the quiz."""
        q = {
            'type': 'single',
            'question': question,
            'options': options,
            'correct': correct_answer,
            'explanation': explanation or f"The correct answer is: {correct_answer}",
            'widget': None  # Will be created when question is displayed
        }
        self.questions.append(q)
        self.total = len(self.questions)
        return self
    
    def add_multiple_choice_question(self, question, options, correct_answers, explanation=None):
        """Add a multiple-choice question to the quiz."""
        q = {
            'type': 'multiple',
            'question': question,
            'options': options,
            'correct': correct_answers,
            'explanation': explanation or f"The correct answers are: {', '.join(correct_answers)}",
            'widget': None  # Will be created when question is displayed
        }
        self.questions.append(q)
        self.total = len(self.questions)
        return self
    
    def display_question(self):
        """Display the current question."""
        if self.current_question >= len(self.questions):
            self.show_final_results()
            return
        
        q = self.questions[self.current_question]
        question_html = f"<h3>Question {self.current_question + 1}/{self.total}</h3><p>{q['question']}</p>"
        self.question_widget.value = question_html
        
        # Create appropriate widget based on question type
        if q['type'] == 'single':
            q['widget'] = widgets.RadioButtons(
                options=q['options'],
                description='Choose:',
                disabled=False,
                layout=widgets.Layout(
                    width='100%',
                    margin='20px 0'
                ),
                style={'description_width': 'initial'}
            )
        else:  # Multiple choice
            # Create a checkbox for each option
            checkboxes = [widgets.Checkbox(description=option, value=False, indent=False) for option in q['options']]
            q['widget'] = widgets.VBox(checkboxes)
        
        # Update display
        if hasattr(self, 'answer_container'):
            self.main_container.children = self.main_container.children[:-1]  # Remove old answer widget
        
        self.answer_container = widgets.VBox([q['widget']])
        self.main_container.children = self.main_container.children[:-3] + (self.answer_container, self.feedback_widget, self.next_button, self.progress_widget)
        
        # Update progress
        self.progress_widget.value = f"<p>Progress: {self.current_question + 1}/{self.total} | Score: {self.score}/{self.total}</p>"
        
        # Update button
        self.next_button.description = "Submit Answer"
        self.feedback_widget.value = ""
    
    def check_answer(self):
        """Check if the current answer is correct."""
        q = self.questions[self.current_question]
        is_correct = False
        
        if q['type'] == 'single':
            selected = q['widget'].value
            is_correct = selected == q['correct']
            
            if is_correct:
                feedback = f"<div style='color: green; padding: 10px; background: #f0fff0; border-radius: 5px;'><b>Correct!</b> {q['explanation']}</div>"
                self.score += 1
            else:
                feedback = f"<div style='color: #cc0000; padding: 10px; background: #fff0f0; border-radius: 5px;'><b>Incorrect.</b> {q['explanation']}</div>"
                
        else:  # Multiple choice
            checkboxes = q['widget'].children
            selected = [q['options'][i] for i, cb in enumerate(checkboxes) if cb.value]
            
            # Check if selected answers match correct answers (order doesn't matter)
            is_correct = set(selected) == set(q['correct'])
            
            if is_correct:
                feedback = f"<div style='color: green; padding: 10px; background: #f0fff0; border-radius: 5px;'><b>Correct!</b> {q['explanation']}</div>"
                self.score += 1
            else:
                feedback = f"<div style='color: #cc0000; padding: 10px; background: #fff0f0; border-radius: 5px;'><b>Incorrect.</b> {q['explanation']}</div>"
        
        self.feedback_widget.value = feedback
        self.next_button.description = "Next Question"
        
        # Disable answer widget to prevent changes
        if q['type'] == 'single':
            q['widget'].disabled = True
        else:
            for cb in q['widget'].children:
                cb.disabled = True
                
        # Update progress
        self.progress_widget.value = f"<p>Progress: {self.current_question + 1}/{self.total} | Score: {self.score}/{self.total}</p>"
    
    def next_question(self, button):
        """Handle the next button click."""
        if not self.quiz_started:
            self.quiz_started = True
            self.display_question()
            return
        
        if self.next_button.description == "Submit Answer":
            self.check_answer()
        else:
            self.current_question += 1
            if self.current_question >= len(self.questions):
                self.show_final_results()
            else:
                self.display_question()
    
    def show_final_results(self):
        """Display the final quiz results."""
        percentage = (self.score / self.total) * 100 if self.total > 0 else 0
        
        if percentage >= 80:
            message = "Excellent work!"
        elif percentage >= 60:
            message = "Good job!"
        else:
            message = "Keep practicing!"
            
        result_html = f"""
        <div style='padding: 20px; background: #f5f5f5; border-radius: 10px;'>
            <h3>Quiz Completed!</h3>
            <p>You scored: {self.score} out of {self.total} ({percentage:.1f}%)</p>
            <p>{message}</p>
        </div>
        """
        
        self.question_widget.value = result_html
        self.feedback_widget.value = ""
        
        # Clear all button click handlers and set new one for restart
        self.next_button.on_click(lambda b: None, remove=True)
        self.next_button = widgets.Button(description="Restart Quiz")
        self.next_button.on_click(self.restart_quiz)
        
        # Remove answer container and update main container
        if hasattr(self, 'answer_container'):
            self.main_container.children = (
                self.title_widget,
                self.question_widget,
                self.feedback_widget,
                self.next_button,
                self.progress_widget
            )
    
    def restart_quiz(self, button):
        """Restart the quiz."""
        self.current_question = 0
        self.score = 0
        self.quiz_started = True
        
        # Clear all button click handlers and set new one for next question
        self.next_button.on_click(lambda b: None, remove=True)
        self.next_button = widgets.Button(description="Next Question")
        self.next_button.on_click(self.next_question)
        
        # Update main container with new button
        self.main_container.children = (
            self.title_widget,
            self.question_widget,
            self.feedback_widget,
            self.next_button,
            self.progress_widget
        )
        
        self.display_question()
    
    def display(self):
        """Display the quiz."""
        display(self.main_container)

# Example usage
def create_sample_quiz():
    # Create a new quiz
    quiz = MCQQuiz(title="Python Programming Quiz")
    
    # Add single-choice questions
    quiz.add_single_choice_question(
        "What is the output of: print(2 ** 3)?",
        ["2", "6", "8", "23"],
        "8",
        "The ** operator performs exponentiation. 2 ** 3 equals 2³ which is 8."
    )
    
    quiz.add_single_choice_question(
        "Which of the following is used to define a function in Python?",
        ["func", "define", "def", "function"],
        "def",
        "In Python, functions are defined using the 'def' keyword."
    )
    
    # Add multiple-choice questions
    quiz.add_multiple_choice_question(
        "Which of the following are valid Python data types? (Select all that apply)",
        ["Integer", "Float", "Character", "Boolean", "Double"],
        ["Integer", "Float", "Boolean"],
        "Python has Integer, Float, and Boolean as basic data types. There's no separate Character type (strings are used instead), and Double is not a distinct type (Float is used)."
    )
    
    quiz.add_multiple_choice_question(
        "Which of these are valid loop structures in Python? (Select all that apply)",
        ["for loop", "while loop", "do-while loop", "until loop"],
        ["for loop", "while loop"],
        "Python supports 'for' and 'while' loops. It does not have built-in 'do-while' or 'until' loops."
    )
    
    # Display the quiz
    quiz.display()
    
    return quiz

def create_kmeans_quiz():
    quiz = MCQQuiz(title="K-means Clustering Quiz")
    quiz.add_single_choice_question(
        "What is the main goal of the k-means algorithm?",
        [
            "To maximize the distance between clusters",
            "To minimize the sum of squared distances within clusters",
            "To sort data points",
            "To reduce dimensionality"
        ],
        "To minimize the sum of squared distances within clusters",
        "K-means aims to minimize the total intra-cluster variance (sum of squared distances between points and their assigned centroid)."
    )
    quiz.add_single_choice_question(
        "What does the 'K' in k-means stand for?",
        ["Number of clusters", "Number of features", "Number of data points", "Number of iterations"],
        "Number of clusters",
        "'K' is the number of clusters you want to find in your data."
    )
    quiz.add_single_choice_question(
        "Which step comes first in the k-means algorithm?",
        ["Update centroids", "Assign points to clusters", "Initialize centroids", "Repeat until convergence"],
        "Initialize centroids",
        "The first step is to randomly initialize the centroids."
    )
    quiz.add_single_choice_question(
        "Which of the following is a limitation of classical k-means?",
        ["It can get stuck in local minima", "It always finds the global optimum", "It works only for supervised learning", "It does not require initialization"],
        "It can get stuck in local minima",
        "K-means can get stuck in local minima depending on the initial centroids."
    )
    quiz.add_multiple_choice_question(
        "Select all that are true about k-means (choose all that apply):",
        ["It is unsupervised", "It requires specifying K", "It always produces the same result", "It uses centroids"],
        ["It is unsupervised", "It requires specifying K", "It uses centroids"],
        "K-means is unsupervised, requires you to specify the number of clusters (K), and uses centroids. Results can vary due to random initialization."
    )
    quiz.display()
    return quiz

def create_quantum_encoding_quiz():
    quiz = MCQQuiz(title="Quantum Data Encoding Quiz")
    
    quiz.add_single_choice_question(
        "Which of the following is NOT a common quantum data encoding method?",
        ["Basis encoding", "Amplitude encoding", "Angle encoding", "Regression encoding"],
        "Regression encoding",
        "Common quantum data encoding methods include basis encoding, amplitude encoding, angle encoding, and phase encoding. Regression encoding is not a standard quantum encoding method."
    )
    
    quiz.add_single_choice_question(
        "In angle encoding, data is typically encoded into:",
        ["The number of qubits", "The phase of quantum states", "The rotation angles of quantum gates", "The probability amplitudes"],
        "The rotation angles of quantum gates",
        "Angle encoding maps classical data values to rotation angles of quantum gates (typically Ry rotations)."
    )
    
    quiz.add_single_choice_question(
        "Which quantum gate is commonly used for angle encoding?",
        ["X gate", "Ry gate", "CNOT gate", "Toffoli gate"],
        "Ry gate",
        "The Ry (rotation around y-axis) gate is commonly used in angle encoding to map data values to rotation angles."
    )
    
    quiz.add_single_choice_question(
        "What is an advantage of amplitude encoding?",
        ["It requires only log(N) qubits to encode N data points", "It is the easiest to implement", "It never requires data normalization", "It is immune to noise"],
        "It requires only log(N) qubits to encode N data points",
        "A major advantage of amplitude encoding is its exponential compression - it can encode N-dimensional vectors using only log(N) qubits."
    )
    
    quiz.add_multiple_choice_question(
        "Which statements about quantum data encoding are true? (Select all that apply)",
        ["Data normalization is often required", "Different encoding methods have different qubit requirements", "The choice of encoding affects the quantum circuit depth", "All encoding methods are equally efficient"],
        ["Data normalization is often required", "Different encoding methods have different qubit requirements", "The choice of encoding affects the quantum circuit depth"],
        "Data normalization is typically required for quantum encoding. Different encoding methods have different qubit requirements and affect circuit depth. Not all encoding methods are equally efficient for all applications."
    )
    
    quiz.display()
    return quiz

def create_quantum_kmeans_quiz():
    quiz = MCQQuiz(title="Quantum K-means Algorithm Quiz")
    
    quiz.add_single_choice_question(
        "What quantum technique is commonly used to measure similarity between quantum states in quantum k-means?",
        ["Grover's algorithm", "Quantum Fourier Transform", "Swap test", "Hadamard test"],
        "Swap test",
        "The swap test is a quantum algorithm commonly used to estimate the overlap between two quantum states, making it useful for measuring similarity in quantum k-means."
    )
    
    quiz.add_single_choice_question(
        "In quantum k-means, which step is typically performed classically?",
        ["Data encoding", "Distance calculation", "Centroid update", "State preparation"],
        "Centroid update",
        "In most quantum k-means implementations, the centroid update step is performed classically after quantum measurement of distances/similarities."
    )
    
    quiz.add_single_choice_question(
        "What does the swap test measure between two quantum states |ψ₁⟩ and |ψ₂⟩?",
        ["The sum of the states", "The probability of measuring |0⟩", "The fidelity |⟨ψ₁|ψ₂⟩|²", "The entanglement entropy"],
        "The fidelity |⟨ψ₁|ψ₂⟩|²",
        "The swap test measures the fidelity (|⟨ψ₁|ψ₂⟩|²) between two quantum states, which quantifies their similarity."
    )
    
    quiz.add_single_choice_question(
        "What is a primary challenge in implementing quantum k-means on near-term quantum hardware?",
        ["Noise in quantum circuits", "Limited number of qubits", "Classical post-processing", "All of the above"],
        "All of the above",
        "Quantum k-means faces multiple challenges on near-term hardware: noise affects measurement accuracy, limited qubits restrict dataset size, and classical post-processing is needed for centroid updates."
    )
    
    quiz.add_multiple_choice_question(
        "Which of the following are potential advantages of quantum k-means? (Select all that apply)",
        ["Potential speedup for high-dimensional data", "Ability to find non-linear clusters naturally", "Complete immunity to noise", "Reduced dependence on initial centroids"],
        ["Potential speedup for high-dimensional data", "Ability to find non-linear clusters naturally"],
        "Quantum k-means potentially offers speedup for high-dimensional data and might better capture non-linear relationships. However, it is not immune to noise and still depends on initial centroids."
    )
    
    quiz.display()
    return quiz

