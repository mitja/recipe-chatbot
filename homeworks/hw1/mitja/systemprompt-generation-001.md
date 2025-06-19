# System Prompt for a Recipe Chatbot for Families

Please help me create a system prompt for a recipe chatbot. Below is a high level concept of the envisioned system, and which features the prompt for the MVP shall have. Please also follow the basic instructions for creating the system prompt.

## Product Idea, Hypothesis, Benefits

### What is the pain with recipes for families?

Good recipes are tedious and hard to create. They must align

  - health and fitness goals like losing weight,
  - balanced nutrition,
  - allergies, food intolerances, or other constraints (eg. vegetarian)
  - convenienience and cost effectiveness (eg. taking local stores and sales into account),
  - desires, tastes, and needs across a family and for friends and family.

### Qualities a great recipe chatbot for families

A great recipe chatbot helps a family create meals which 

  - are loved by the family members,
  - are healthy for them,
  - are convenient to prepare and shop for, and
  - fit into their time and money budgets,
  - can flexibly adapt to life as it happens.

### Components of a great recipe chatbot for familes

A chatbot for ad-hoc recipes is helpful, but cannot effectively meet all these requirements. It can eg. help create a based on what's in the fridge, but asking all the aspects for each recipe, would be too cumbersome to use. Thus, a great recipe chatbot must have means to:

 - store a families' preferences, needs, etc.
 - import offers from local stores (eg. by reading flyers)
 - import other data (eg. nutrition app, health app)
 - plan for more meals in advance (eg. a weekly schedule)
 - keep track of recent meals to avoid repetition
 - keep track of feedback to improve the recommendations for a family over time

### Development Constraints

This recipe chatbot is being developed during a course on AI evals. The objective in context of this course, is to learn how to evaluate AI pipelines. It shall start with a simple prompt and improve the prompt over time. The focus is more on the eval-loop, than on the pipeline. So the question is:

How can I best start the development of this app from a simple prompt and still get on track to the envisioned system?

I see basic approaches to simplify the chatbot development during the course:

1) Limit features, eg. focus only on tastes, leave nutrition aside.
2) Limit fidelity, eg. use only calories and not macros or micros for nutrition.
3) A mix of limited features and fidelity.

This is basically a product management decision:

**What is the MVP of a chatbot that represents the envisioned product well enough to test the main hypthesis, that there is a demand for such a product?**

### MVP hypothesis and required features and fidelity

The hypothesis is:

**There is market demand for a recipy chatbot for families that helps them create menuplans for healthy and tasty meals.**

Based on that:

- taste and loved by the family is the foundation
- health and nutrition awareness is important (assumed: higher willingness to pay)
- weekly perspective is important (assumed: this is a differentiator to basic recipe chatbots)
- convenience and budgets nice to have (shopping lists, budget, etc. are nice to have and can be dropped, at first).
- fidelity must be tuned down a bit as this the must and important aspects to reduce work.

This leads to main benefits that can also be achieved with a MVP.

### Benefits

- Relieve stressful thinking about menues day-to-day with weekly menuplans.
- Shop faster with clear shopping lists for a week.
- Save time with fewer ad-hoc shopping trips.
- Eat healthy without beancounting calories and macros.
- Stay flexible for surprise guests and invitations with easily adaptable plans.

## Prompt Engineering

### What good results look like? (how the chatbot should behave)

- take tastes, nutrition demands, convenience, costs, and variety into account
- make a plan for the week
- use recipies that are from trusted sources, or tried
- make a shopping list
- calculate the volumes, according to our needs, adjustable for invited friends or surprise guests
- balance variety and familiarity
- suggest new recipies from time to time
- recommend adjusting meals / recipies according to demands
- take feedback into account

### What bad results look like? (how the chatbot should not behave)

- repeatedly suggest meals we don't like, should not eat, are hard for us to shop for and prepare, are too costly
- too rigid - better suggest some I can chose from (gradually enhanced, eg. meals with things I have at home, vs. where I can quickly buy)
- create recipies that don't work (eg. adapting volumes of proven/known recipies are better than generating recipes from scratch)
- calculate with wrong/halucinated assumptions (Eg. nutrition data, cross-allergens)
- use dangerous ingredients


## Prompt Development Instruction

Please help me create an LLM prompt for a recipe chatbot for health concious families. The prompt will be used as the system prompt in a recipe chatbot MVP. In the first iteration, it does not have any supporting services like recipe database, meal history, nutrition database, nutrition demands and food constraints. 

Please create a system prompt based on best practices.

Include includes static-like example data in special sections (eg. enclosed by XML tags):

- recipes list with ingredients for 3 persons
- nutrition data
- high-level calory, macro nutrition budget and food constraints for three family members:
  - father: 53, 180cm, 92kg, wants to lose weight, sedentary, no pork, low red meat, but enough protein, still
  - mother: 50, 154cm, 42kg, normally active
  - daughter: 12, 149cm, slim, active, wants to grow
- example data about favorite recipes for each
- meal history (eg. 14 days) for variety
- list of available food "in the fridge"
- last meal plan (7 day-plan, rolling update)

Let the LLM gather the required up-to-date information by asking the user:

- what the user ate today
- ask if there are guests or if a family member eats outside (today or the next few days)
- tell the planned recipe for today
- if the user asks for another recipe: suggest recipes and let the user select one

As output:

- output the recipe with adapted volumes if necessary
- provide nutrition info
- an updated meal plan for the upcoming 7 days
- an updated shopping list

Let the LLM generate the output in structured format, please suggest a good format for the most important outputs for inclusion in the prompt.
