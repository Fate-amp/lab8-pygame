# Project Report: AI-Assisted Development

## 1. Initial Approach
* **Understanding:** Briefly describe your strategy for tackling the requirements.
I experimented more what I discovered on the fleeing feature. So I started using CoPilot to understand
before I started coding and this helped me a lot more than when I coded first and then started debugging.
Then, I generated the code-explorer and started refactoring

* **Assumptions:** What did you assume about the project before starting?
Although it seemed easy to tackle, it wasn't intuitive at first. For example, I knew I had to track the time and change the screen based on it but when I got to implementing it, I was stuck. Which is the main part where I used CoPilot on. To understand and to improve.

## 2. Prompting & AI Interaction
* **Successes:** What types of prompts or context worked best for you?
I liked exploring with the code-explorer. This was something that was missing from my work: refactoring. Before, I did not know how to do that or where to start, but using the performance tab and the code review, I got ideas on where to start.

* **Failures:** Describe specific instances where CoPilot failed (hallucinations, over-engineering, or logical errors).
Well, there was some instance where Codex's socratic mode was not answering questions at all and instead asking 10 questions at a time, and I had to change the model and ask it explicitely that I want details and hints not just questions

Also, there was one instance when Haiku suggested something without keeping in mind the edge cases, and if I didn't prompt it in order to improve, it would have resulted in a buggy code

**Problem**: Before refactoring the code, I was getting this moderate risk that the complexity is O(n^2), but now that it's O(n), it shows high risk!

* **Analysis:** Why do you think these failures happened, and how did they impact your progress?
I'm guessing my prompt was vague and even with powerful models(I was on auto most of the time in this project), I might not get what I want or as good as I want it

## 3. Key Learnings
* **Technical Skills:** What CS concepts or tools did you discover or master during this project?
The code-explorer was the main new thing I explored which really felt like a senior looking over your code, I can see how it would be of great help in big projects as it helps prevent bugs and edge cases and complexity issues which would be costly after production

* **AI Workflow:** How will you change your use of AI tools in your next project?
I would ask questions until I understand the requirments well but that's not really new as I've already started doing that.
The main thing I would do differently is that I would put some time aside for refactoring with code-explorer

I found out that while refactoring, I can learn as much as the coding itself