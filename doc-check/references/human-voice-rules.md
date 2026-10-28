# The human-voice rules

This file gives the human-voice rules.
Each rule removes one sign of AI writing.
The signs come from Wikipedia ("Signs of AI writing"), AI detector guides, humanizer tools, and arXiv studies.
Each rule has an ID, and `scripts/voice_check.py` gives these IDs when it reports an error.

The basic rule is this: write the specific fact in plain words, then stop.
All the other rules are parts of the basic rule.

## How to apply the rules

- Apply all the rules to all the prose that you write when this skill is active.
- There are two text types:
  - STE text is the text in the STE scope of SKILL.md.
  - Free text is all other prose: conversation, letters, articles, posts, and stories.
- In STE text, the STE rules win when a rule here does not agree with them. STE text has no contractions (rule 4.2), only complete sentences (rule 4.1), and the STE word limits.
- Rules V2 and V3 apply only to free text.
- In a procedure, all the steps have the same form (rule 9.4). The rhythm rules V1 and V4 apply to the descriptive paragraphs.
- The rules do not control code, commands, quoted text, or official names.
- Each rule is mandatory. If a rule makes a sentence wrong, write a different sentence.
- In the examples, "Not" shows the AI sign. "Write" shows the correct text. The "Write" examples are free text.

## 1. Rhythm (V)

- V1. Vary the sentence length over the full text. Let the content decide the length of each sentence: a long sentence for a cause and its result, a short sentence for a plain fact. The burstiness must be 35 or more in free text and 25 or more in STE text. Burstiness is the standard deviation of the sentence lengths, divided by the mean length, times 100. Do not add a short sentence only to change the rhythm. A short "pivot" sentence such as "The real risk is narrower." is an AI sign.
  - Not: "The system reads the data. The screen shows the result. The design keeps the cost low."
  - Write: "The system reads the data and shows the result on one screen, so nobody has to open a second window. That's the whole design."
- V2. In free text, use contractions where a speaker uses them: "it's", "don't", "can't", "you'll", "that's", "isn't". Write the full form only for emphasis. Use one contraction or more in each 100 words.
  - Not: "It is late and we do not have the logs."
  - Write: "It's late and we don't have the logs."
- V3. In free text, a short fragment of 4 words or fewer is permitted, but it is not required. Write one only where a speaker says it naturally: a direct answer to a question that the reader asked, or a result in a sequence of events. Write one fragment in a paragraph at most, and never two in sequence. These fragments are AI signs, so do not write them:
  - A label and a short value: "Cause: the migration." "Result: no shared codec."
  - A repeat of the number in the sentence before it: "Less than half."
  - A time or a date split off from its sentence: "Next Tuesday, 06:00."
  - A dramatic closer (refer to S8).
  - Write: "We tried the cache fix first. No change. The real cause was a DNS timeout, which we found an hour later in the resolver log."
- V4. Vary the paragraph length. Mix paragraphs of one or two sentences with longer paragraphs. In a text of four or more paragraphs, the paragraph lengths must not be almost equal.
- V5. Use the punctuation that the meaning needs: commas, periods, colons, parentheses, and question marks. In free text of 300 words or more, use one mark or more that is not a comma or a period. Use a comma, a colon, parentheses, or a new sentence where AI text puts a dash. Never use an em dash, an en dash, or "--" as a dash. For a range, write "10 to 20".
  - Not: "The answer, and it surprised everyone, was simple." with dashes around the middle part.
  - Write: "The answer surprised everyone. It was a missing index."
- V6. Keep one voice in the full text. If the user gives a sample of their writing, match its sentence length, its contractions, and its punctuation.
- V7. Correct all grammar errors. The human voice comes from these rules. It does not come from errors.

## 2. Words (W)

- W1. Use the plain, common word. Replace each word in the W1 list (section 9) with a plain word or a specific fact.
  - Not: "The study delves into the intricate interplay of soil factors."
  - Write: "The study measures how pH and moisture change root growth."
- W2. Name the thing that the product or the person does. Replace each buzzword with that action.
  - Not: "Our platform empowers teams to seamlessly leverage cutting-edge tools."
  - Write: "The app syncs calendars between Outlook and Google every five minutes."
- W3. Use "tapestry", "landscape", "beacon", "journey", and "realm" only with their literal meanings.
  - Not: "The city is a rich tapestry of cultures."
  - Write: "About 180 nationalities live in Brussels."
- W4. Use an adverb only when it changes the fact. Remove "quietly", "deeply", "fundamentally", "truly", and "incredibly".
  - Not: "Spreadsheets quietly run the economy."
  - Write: "Most small firms do their accounts in spreadsheets."
- W5. Describe places and products with neutral words, as a reference book does.
  - Not: "Nestled in the heart of the valley, the village boasts a rich heritage."
  - Write: "The village is in the Semois valley and has a 12th-century church."
- W6. Use "is", "are", and "has" for a simple fact.
  - Not: "The library serves as a hub and features 40,000 books."
  - Write: "The library has 40,000 books and is open until 22:00."
- W7. Use plain verbs. Use "said" for speech, and use it again each time. Use "wrote" and "died".
  - Not: "'We're late,' the manager noted."
  - Write: "'We're late,' the manager said."
- W8. Use one name for one thing in the full text (STE rule 1.11). Use the same noun again, or a pronoun.
  - Not: "the app ... the platform ... the tool ... the solution"
  - Write: "the app ... the app ... it"
- W9. Select each verb and adjective for its precise meaning. Do not use a striking word again later as a callback.
  - Not: "That's where the friction lives. ... Remove the friction and growth follows."
  - Write: "Sign-up takes nine screens. Cut it to three and more people finish."
- W10. Give a concept a name only if you define the name at its first use and use the name again.
  - Not: "This is what I call the visibility trap."
  - Write: "Managers can't see the work, so they add meetings to see it."
- W11. Write a hyphenated modifier only before a noun, and only to prevent a wrong meaning. Write one in each sentence at most.
  - Not: "a high-quality, data-driven, future-proof approach"
  - Write: "an approach that cut defects by half"
- W12. Use a connecting word only where the logic needs it. Use "and", "but", "so", "then", or no connecting word. In STE text, use "thus" one time in a text at most.
  - Not: "Additionally, it's worth noting that costs rose."
  - Write: "Costs rose too."

## 3. Claims and content (C)

- C1. Give the fact and its measured result. Say that a thing is important only with a source.
  - Not: "Its 1998 opening marked a pivotal moment for the town."
  - Write: "It opened in 1998, and tourist numbers doubled in five years."
- C2. Keep the stakes at their real size.
  - Not: "This will fundamentally reshape how we think about work."
  - Write: "This saves each team about two hours a week."
- C3. Stop the sentence when the fact stops. If a result is real, give it its own sentence and its source. Do not add a clause with an "-ing" verb that adds meaning without evidence.
  - Not: "The bridge opened in 1932, symbolizing the region's resilience."
  - Write: "The bridge opened in 1932."
- C4. Name the source: the person or the organization, the document, and the year.
  - Not: "Experts argue that remote work changed company culture."
  - Write: "Bloom and colleagues (Nature, 2024) found that hybrid work at Trip.com cut resignations by a third."
- C5. Show that a subject is notable with a fact about it. Do not give a list of media outlets.
  - Not: "She was featured in Forbes, Wired, and other leading outlets."
  - Write: "Her 2022 paper on TCP congestion control is cited in the IETF draft."
- C6. Use the verb that gives the exact relation: founded, led, owns, played in.
  - Not: "He is associated with the orchestra."
  - Write: "He founded the orchestra in 1994."
- C7. Give problems as facts. End with the current condition, not with an optimistic turn.
  - Not: "Despite these challenges, the festival continues to thrive."
  - Write: "Attendance fell from 12,000 to 8,000 after 2023, and the 2027 festival has no sponsor yet."
- C8. Give the specific data that an expert expects: numbers, names, dates, versions, and sample sizes.
  - Not: "The method significantly improves accuracy across many tasks."
  - Write: "The method raised accuracy from 71% to 78% on three of the five benchmarks."
- C9. Give each claim the confidence that its evidence supports. Give a measured fact directly, with its number. Give the scope of a general claim.
  - Not: "Every successful company relies on data-driven decisions."
  - Write: "Of the 40 firms in the survey, 31 review sales data each week."
- C10. Qualify an uncertain claim one time, and give the reason.
  - Not: "This could potentially help, to some extent, in certain cases."
  - Write: "This probably helps on small files. We didn't test files over 1 GB."
- C11. Give your position when you have one.
  - Not: "On the one hand, AI saves time. On the other hand, it raises concerns."
  - Write: "AI drafts save us time, but we rewrite every customer email by hand."
- C12. If you do not know a fact, say so in one sentence and stop. Do not guess what is "likely".
  - Not: "Though her early life isn't widely documented, she likely grew up in Ghent."
  - Write: "I couldn't find a source for where she grew up."
- C13. Correct a claim only when a person made that claim.
  - Not: "The data does not establish contamination. Treat it as a baseline rather than a verdict."
  - Write: "The samples show lead at 4 µg/L, below the 10 µg/L limit."
- C14. Answer an objection only when a person gave that objection.
  - Not: "To be clear, I'm not saying meetings are useless."
  - Write: Remove the sentence.
- C15. Give each point one time. Do not say it again in different words, and do not copy a passage.
- C16. Write about the subject, not about the document.
  - Not: "The table below compares the options. Anything unconfirmed is flagged."
  - Write: Give the table. Write "unconfirmed" in each cell that has no confirmation.
- C17. Do not tell the reader what the reader told you.
  - Not: "So, to answer your question: yes, you can add the user."
  - Write: "Yes. Open Settings, then Users, then Add."
- C18. Start with the point, not with a definition.
  - Not: "Burnout is a state of emotional, physical, and mental exhaustion."
  - Write: "Half the support team reported burnout in the March survey."
- C19. Quote only words that a person said or wrote, from a source that you have. Keep quotes short. Give a title such as "Dr." only when the source gives it.
  - Not: "'This represents a significant step forward,' said Dr. Ruiz." (no source)
- C20. Show the evidence, and let the reader find the meaning.
  - Not: "She cried, which shows how deeply the loss affected her."
  - Write: "She cried for the rest of the drive."
- C21. Include the detail that a generic text does not have: an example from this case, an opinion, a number.
  - Not: "Coffee is a popular beverage enjoyed by millions worldwide."
  - Write: "The office uses 4 kg of coffee a week, mostly before ten."
- C22. Use one standard for all governments, companies, and persons. Use the same verbs for the same actions.
- C23. Add no fact that the user did not give and that a source does not support. Do not add a policy, a number, a step, a quote, or a scenario to reach a length target. A shorter text is correct. If an inference is useful, mark it as an inference.
  - Not: "We don't deliver outside Ghent." (The user said only that delivery in Ghent costs 4 euros.)
  - Write: "Delivery in Ghent costs 4 euros."

## 4. Sentence structure (S)

- S1. Give the positive claim directly. Do not write "not X, but Y" or "it's not X, it's Y". The same applies across two sentences ("The fix was not a new tool. It was two habits.") and to a trailing contrast ("The lock was the problem, not the schema change.").
  - Not: "It's not just a tool, it's a mindset."
  - Write: "The tool cuts review time by half."
- S2. Use "and" to join two facts. Do not write "not only ... but also".
  - Not: "The plan is not only affordable but also scalable."
  - Write: "The plan costs 40 euros a month and supports 10,000 users."
- S3. Write "rather than" or "instead of" only when the reader expects the other option.
  - Not: "It prioritizes trust rather than speed."
  - Write: "It asks for confirmation before each payment."
- S4. Give the true statement. Do not write a sequence of negatives before it.
  - Not: "Not a bug. Not a feature. A design flaw."
  - Write: "The timeout is too short for slow networks."
- S5. Write the real number of items. Two items are correct. Four items are correct. Write three items only when there are three. Write one list of three in a paragraph at most.
  - Not: "The workshop was engaging, informative, and inspiring."
  - Write: "The workshop showed us how to read a SIP trace."
- S6. Write "from X to Y" only for a real scale: dates, sizes, or numbers.
  - Not: "From strategy to execution to culture, everything changes."
  - Write: "Prices rose from 4 to 6 euros between 2023 and 2025."
- S7. Make a statement. Ask a question only when you want the reader to answer it.
  - Not: "The result? Chaos."
  - Write: "The release broke the login page for two hours."
- S8. Write fragments only as V3 tells you. Do not stack fragments for effect. Do not end a text with a dramatic one-line closer.
  - Not: "He shipped it. Alone. In a weekend."
  - Write: "He wrote and shipped the parser alone over one weekend."
- S9. Give the specific point. Do not write a sentence that sounds wise and says nothing, and do not announce a lesson ("The lesson I keep coming back to").
  - Not: "At its core, leadership is about trust."
  - Write: "The team lead signs off each release herself."
- S10. Start sentences in different ways. Start two sentences in sequence with the same word at most.
  - Not: "They assume users will pay. They assume devs will build. They assume..."
  - Write: "The plan assumes users will pay and developers will build, but nobody has asked either group."
- S11. Start with the content. Do not announce it first.
  - Not: "Here's the thing about pricing: nobody reads it."
  - Write: "Nobody reads the pricing page."
- S12. Give the list without its count in front.
  - Not: "Here are five key takeaways."
  - Write: Give the five items.
- S13. Explain directly. Use an analogy only when the reader cannot understand without it.
  - Not: "Think of an API as a waiter carrying orders to the kitchen."
  - Write: "An API is a set of URLs that a program can call to read or change data."
- S14. Support a point with evidence, not with a sequence of famous company names.
  - Not: "Apple didn't build Uber. AWS didn't build Airbnb."
- S15. Do not perform honesty.
  - Not: "And yes, I'll admit it: I'm obsessed with spreadsheets."
- S16. Give the content. Do not describe your reasoning or the moves of the text.
  - Not: "What this changes is smaller than it seems, and worth being precise about."
  - Write: "This changes one default: the timeout goes from 30 to 60 seconds."
- S17. Give the claim first, then the evidence.
- S18. End a sentence on its main clause.
  - Not: "Paste it above the footer, and save."
  - Write: "Paste it above the footer and save the file."
- S19. Stop after the last point. Do not add clause after clause at the end.
- S20. Use verbs, not nouns made from verbs. Make a noun the subject, not a "that" clause.
  - Not: "The implementation of the optimization resulted in an improvement."
  - Write: "We changed the query, and it runs three times faster."
- S21. Make the agent the subject (STE rule 3.6).
  - Not: "Results are preserved automatically."
  - Write: "The tool saves the results."
- S22. Give the location of a thing with a real location.
  - Not: "That's where the complexity actually lives."
  - Write: "Most of the complexity is in the billing module."

## 5. Text structure (T)

- T1. Use the concrete word over the expected word. A predictable sentence is an AI sign.
  - Not: "Exercise is important for maintaining good health and overall well-being."
  - Write: "Twenty minutes of walking a day lowered blood pressure in the trial group."
- T2. Vary the sentence structure, not only the length. Do not use one sentence pattern again and again.
  - Not: "Speed is vital because users leave. Cost is essential because margins are thin."
- T3. Do not write summary sentences or summary sections. End on the last new fact or on the next action.
  - Not: "In conclusion, the future of AI depends on..."
- T4. Give new information in the first sentence after a heading. Do not repeat the heading.
- T5. Use prose for connected reasoning. Use a list only for parallel items: steps, options, or data. Do not put "The first ..., The second ..." in prose.
- T6. Use headings only in a text of more than approximately 400 words. A short answer has no headings.

## 6. Format (F)

- F1. Use straight quotes and straight apostrophes (" and ') in plain text, code, and chat.
- F2. Use words, not symbols. Write "then" or "to", not an arrow. Write "yes" or "no", not a check mark.
  - Not: "Input → Process → Output"
  - Write: "The program reads the input, processes it, and writes the output."
- F3. Write prose without bold. Use bold only for WARNING, CAUTION, and the labels of controls that the reader must find.
- F4. Start each list item with plain text. Do not start a list item with a bold label and a colon.
- F5. Write headings in sentence case: "Impact of technology on society".
- F6. Do not put emoji in headings, lists, or technical text. In chat, use emoji only if the user uses them.
- F7. Write a heading as the name of its topic. Do not start a heading with "Why", "What", or "Where".
- F8. Use a table only for data that the reader compares, with three rows and two columns or more. Put a smaller set of data in a sentence.
- F9. Use Markdown only where Markdown shows correctly. In plain text, email, Word, or wikitext, use the markup of that format.
- F10. Use heading levels in sequence. Put text under each heading. Do not repeat the document title as a heading. Do not put a horizontal line between all sections.
- F11. Remove all tool artifacts: "oaicite", "contentReference", "utm_source=", "<mark>", the "↩" mark, and "continue generating".
- F12. Fill each placeholder, or ask the user for the data. Do not leave "[Insert name]", "2025-XX-XX", or "Your Name" in the text.

## 7. Chatbot residue (R)

- R1. Start with the answer. Stop when the content stops. Do not praise the question, do not offer more help at the end, and do not end a post with a request for comments.
  - Not: "Great question! ... I hope this helps. Let me know if you'd like changes."
- R2. Give the fact without a disclaimer in front of it. If the fact is a risk, write a WARNING or a CAUTION.
  - Not: "It's important to note that laws vary by country."
  - Write: "Belgian law requires a written contract. Dutch law doesn't."
- R3. Do not mention a knowledge cutoff or that you are an AI. If data can be old, give the date of the data.
  - Not: "As of my last update, no data exists."
  - Write: "The newest data I found is from March 2026."
- R4. Complete each sentence and each section.
- R5. Do not start with "Below is", "Certainly", "Based on the text", or "According to the provided".
- R6. Report a change by its result.
  - Not: "Preserved references, ensured a neutral tone, improved verifiability."
  - Write: "Moved the 2019 results into the History section and fixed two dead links."
- R7. Do not put notes to a reviewer in the deliverable.

## 8. Citations (Q)

- Q1. Cite only sources that you opened in this session. Never write a reference from memory.
- Q2. Make sure that each DOI goes to the cited paper and that each ISBN checksum is correct.
- Q3. Cite a source only for a claim that the source makes. Read the passage before you cite it.
- Q4. Give the page, the section, or the URL for each book or long document.
- Q5. Make sure that each link opens. Replace a dead link with an archived copy, or remove the claim.
- Q6. Give the real access date. Define only the references that you cite.

## 9. Forbidden strings

`scripts/voice_check.py` reads this list.
Each line gives a rule ID and its strings, and a line with "re:" gives a Python regular expression in place of the strings.
The tool ignores case. Technical names are permitted: use `--allow` for them (for example `--allow robust` for "robust standard errors").

<!-- forbidden:start -->
```text
W1: delve, delves, delved, delving, intricate, intricacies, meticulous, meticulously, underscore, underscores, underscored, underscoring, showcase, showcases, showcased, showcasing, garner, garners, garnered, vibrant, robust, interplay, enduring, crucial, comprehensive, multifaceted, bolster, bolstered, foster, fosters, fostered, fostering, enhance, enhances, enhanced, enhancing, align with, aligns with, resonate with, resonates with, valuable insights, deep dive, plethora, myriad, a multitude of, embark, embarks, unwavering, commendable, noteworthy, paramount, navigate the
W2: leverage, leverages, leveraged, leveraging, seamless, seamlessly, unlock, unlocks, unlocking, empower, empowers, empowering, game-changer, game-changing, cutting-edge, state-of-the-art, synergy, synergies, best-in-class, world-class, next-level, revolutionize, revolutionizes, revolutionary, transformative, holistic, streamline, streamlines, elevate, elevates, supercharge, harness the, in today's fast-paced, in today's digital, in today's world, ever-evolving, ever-changing, paradigm shift, move the needle, actionable insights
W3: tapestry, landscape, beacon, realm
W4: quietly, deeply, fundamentally, truly, incredibly, profoundly, undeniably, remarkably
W5: nestled, boasts, boasting, breathtaking, stunning, renowned, must-visit, in the heart of, rich heritage, rich history, rich cultural, natural beauty, hidden gem, diverse array
W6: serves as, serve as, served as, stands as, stood as, functions as
W12: additionally, furthermore, moreover, notably, it's worth noting, it is worth noting, worth mentioning, importantly, interestingly
C1: pivotal moment, key turning point, marks a turning point, indelible mark, setting the stage, sets the stage, a testament to, evolving landscape, focal point, deeply rooted, lasting legacy, enduring legacy, broader trends, plays a crucial role, plays a vital role, plays a pivotal role, plays a key role
C2: fundamentally reshape, reshape how we, changes everything, change everything, revolutionize the way
C3 re: ,\s+(?:highlighting|underscoring|emphasizing|symbolizing|reflecting|showcasing|fostering|cultivating|contributing to|ensuring|cementing|solidifying|paving the way)\b
C4: experts argue, experts say, experts believe, observers note, observers have, studies show, research shows, research suggests, critics argue, some critics, many believe, it is widely believed, industry reports
C5: active social media presence, leading outlets, independent coverage
C6: associated with, in connection with
C7: despite these challenges, despite its challenges, despite the challenges, the future looks bright, continues to thrive, challenges and legacy, future outlook
C10: could potentially, may potentially, might potentially, could possibly, might arguably, to some extent
C11: on the one hand
C12: not widely documented, based on available information, limited information is available, not publicly available, it is believed that
C13: does not establish, should not be confused with, should be treated as
C14: to be clear, don't get me wrong, i'm not saying, i am not saying, make no mistake
C16: the table below, the list below, as shown below, in this article, in this section, this guide will, this article will
C17: to answer your question
S1 re: \bnot (?:just|only|merely|simply) (?:about )?[^.?!]{1,60}?[,;]? (?:but|it's|it is)\b
S1 re: \b(?:it's|it is|this is|that's) not (?:about |just )?[^.?!]{1,50}[,;.] (?:it's|it is|this is|that's)\b
S1 re: \b(?:isn't|is not) (?:about|just) [^.?!]{1,50}[,;.] (?:it's|it is)\b
S1 re: \b(?:is|was|are|were|isn't|wasn't|aren't|weren't) not [^.?!]{1,60}\. (?:it|this|that|they) (?:is|was|are|were)\b
S1 re: \b(?:isn't|wasn't|aren't|weren't) [^.?!]{1,60}\. (?:it|this|that|they) (?:is|was|are|were)\b
S1 re: \b(?:is|was|are|were) the [^.,;?!]{1,40}, not (?:the |a )?[^.,;?!]{1,40}[.!]
S2 re: \bnot only\b[^.?!]{1,80}\bbut also\b
S9: at its core, the real question is, what really matters, at the end of the day, the heart of the matter, the bottom line is, the lesson i keep coming back to, the lesson here, the takeaway, the real risk is, the real problem is, the real issue is, the real reason is, the bigger reason is, the bigger risk is
S11: here's what i learned, here is what i learned, here's what happened, here is what happened, here's the thing, here's the kicker, let's dive in, let's dive into, dive into, let's break this down, let's break it down, here's what you need to know, let's explore, let's take a look, without further ado, buckle up, honestly?
S12 re: \bhere are (?:the )?\w+ (?:key |main |essential |important )?(?:ways|things|reasons|takeaways|tips|lessons|insights)\b
S13: think of it as, think of it like, imagine a world, picture this
S15: i'll admit, i'll be honest, full disclosure
S15 re: \band yes, i'll\b
S22: actually lives, really lives
T3: in summary, in conclusion, to sum up, to summarize, as we've seen, all in all, in a nutshell
T3 re: (?:^|[.!?]\s+)overall,
R1: i'd like to hear, i would like to hear, in the comments, share your thoughts, great question, i hope this helps, let me know if, would you like me to, feel free to, happy to help, i'd be happy to
R2: it's important to note, it is important to note, important to remember, keep in mind that, it should be noted
R3: as an ai, as a language model, my last knowledge update, my last training, my knowledge cutoff, as of my last update
R5: below is a, here is a detailed, based on the provided, according to the provided, certainly!, absolutely!
R6: preserved references, ensured that, neutral tone, encyclopedic tone, improved verifiability
```
<!-- forbidden:end -->
