# Project Report: AI-Assisted Development

## 1. Initial Approach
* **Understanding:** Briefly describe your strategy for tackling the requirements.

What I did very differently compared to the previous projects is that I spent most of the time on understanding what was being asked and how pygame worked so unlike the last projects, about 60% of the time was not spent on coding but learning.

* **Assumptions:** What did you assume about the project before starting?

It seemed abstract and not at all intuitive, probably because this is my first experience with pygame and actually implementing what I learned about vectors on a real project.

## 2. Prompting & AI Interaction
* **Successes:** What types of prompts or context worked best for you?

To be very specific, using Claude Haiku 4.5 to understand the requirements in depth. Among the models I've tried Haiku has been the most helpful one with regards to learning.
Also, the socratic mode works best when you actually know what you're doing and it helps you move forward rather than being an obstacle

* **Failures:** Describe specific instances where CoPilot failed (hallucinations, over-engineering, or logical errors).

Some models(even Haiku) don't update the journal automatically and I had to spend valuable auto requests turning the agent back on or fix the many null values logged in it.
But in general, I didn't have any hallucination experience this time around(probably because I used AI mostly to learn and help me with bugs, not generate code)

* **Analysis:** Why do you think these failures happened, and how did they impact your progress?

The challenge about journal logger is not easy to tackle because I don't know how agents work but like any other hallucination which happens because of a knowledge gap, I'm guessing there was some edge cases not handled in the instructions?

## 3. Key Learnings
* **Technical Skills:** What CS concepts or tools did you discover or master during this project?

I learned how to work with and manipulate vectors in terms of an actual program and not just in maths class which helped me link maths concepts I learned about very recently to programming.
Also, the project allowed me to learn pygame in a limited amount of time, how frames, flip and clock work(which seemed very abstract before)
And also, I learned something interesting that helped me tackle pygame during class and that was asking CoPilot to generate a report on how it created the initial setup of the program. I didn't know that was an option before.

* **AI Workflow:** How will you change your use of AI tools in your next project?

I will ask questions until I understand the requirements very well. Because that minimized my debugging on this project
Also, I will use Haiku to create a report for me on generated code, explaining the steps and the "why"s and the program's life cycle