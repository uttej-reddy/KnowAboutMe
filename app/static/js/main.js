// Ask Question
async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const answerSection = document.getElementById('answerSection');
    const question = questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    try {
        answerSection.innerHTML = '<p>Thinking...</p>';
        answerSection.classList.add('active');

        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (response.ok) {
            let html = `
                <div class="answer">
                    <p>${data.answer.replace(/\n/g, '<br>')}</p>
                </div>
            `;

            answerSection.innerHTML = html;
        } else {
            answerSection.innerHTML = `<p class="error">Error: ${data.detail}</p>`;
        }
    } catch (error) {
        answerSection.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Set Question (from sample questions)
function setQuestion(question) {
    document.getElementById('questionInput').value = question;
    document.getElementById('questionInput').focus();
}

// Allow Enter key to submit question
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
