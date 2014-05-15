Dear friend!

Maybe, there are not so much
substances, reactions and levels as you want
in the application now.

But is is very easy to make your own modifications!

Go to "/data/data_substances.txt" if you want to add 
new substance. Each substance is described by two lines:
the first should contain the name of the substance
(which will be 'displayed' on the flask) and the second - 
its color (in the format 'rgb', each component between 0 and 1).
It is obligatory to leave a blank line 
between descriptions of two substances.

Go to "/data/data_reactions.txt" if you want to add 
new reaction. Each reaction is described by three lines:
first two of which should contain names of the reagents
and the third - products of the reaction 
(if there are several products separate them by a whitespace)
It is obligatory to leave a blank line 
between descriptions of two reactions.

Files in "/data/levels/" describe all levels. 

i-th line of "goals.txt" will be displayed as a task  
for the i-th level.

i-th line of "substances.txt" enumerates all substances
which may appear on the conveyor during the i-th level.

i-th line of "tutorials.txt" will be displayed as a tutorial  
for the i-th level. Note, that '\' is used as a newline 
character if your tutorial is multi-line.
Also, [i]text[/i] will apply italic style to the text,
and [b]text[/b] will print the text in bold.

"stage_requirements.txt" describes what user should do
to complete i-th level. Each level is described on two lines.
The first of them contains a number 'k' 
that means user should get k different substances out of
the list given on the second line. 
It is obligatory to leave a blank line 
between descriptions of two levels.

Note, that these 4 files should describe the same number of levels.

So, you can create your own learning/rehearsing base
which will help you:
- to study chemistry;
- to test your students if you are a teacher;
- just to improve your memorizing skills.

Feel free to ask any questions, to report all issues,
to suggest your ideas how to improve the application.
Just send a message to malinovsky239@yandex.ru

Also, I will be glad if you share with me
bases created by yourself.

