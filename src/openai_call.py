from openai import OpenAI


def get_folder_name(name_mapping, question_text, model_name="gpt-3.5-turbo"):
    # # "gpt-4-0125-preview", "gpt-3.5-turbo"
    client = OpenAI()

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Use the following step-by-step instructions to respond to user inputs."
                + "Step 1: Match the question to the corresponding lecture and the learning objective slug. You might see some question unrelated to the lecture (e.g., what did you learn in the lecture), use the slug 'others'. Note that the verb in the objective is important to take into consideration. "
                + "Step 2: Create a slug and a title for the provided question. The question title is a short summary (no more than one sentence, do not use punctuation marks). The purpose of the title is to distinguish the question from other questions, so do not to repeat the learning objective or the question itself. For example, a question title can be 'Fibonacci function' or 'Fill missing data in grades data'. Only capitalize the first letter of a sentence. A slug is a short label for the question, containing only letters, numbers or hyphens. Do not use underscores for slug."
                + "The final output should have the format: 'lecture_objective_slug\nquestion_slug\nquestion_title'. The outputs are separated by new lines. For example, 'lec6_function-test/obj1_function-definition\nadd-10\nImplement a function to add ten' or 'others\nwhat_do_you_learn\nWhat do you learn in lecture' for unrelated questions.",
            },
            {
                "role": "user",
                "content": "You are provided with the slugs for lecture and learning objective, and descriptions (delimited with XML tags): <learning objective> {} </learning objective>. The question is (delimited with XML tags): <question> {} </question>".format(
                    name_mapping, question_text
                ),
            },
        ],
        model=model_name,
    )
    return completion.choices[0].message.content
