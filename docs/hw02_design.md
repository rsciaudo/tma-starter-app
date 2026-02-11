## Team Smarties Design Document - Homework 2

The main decision we had to make was how we were going to track the completion of posts, modules, and courses across 
different users. Initially, we considered using one "completed" table to store the IDs of posts, modules, and courses, and 
find everything a user has completed by performing a join on their ID. The benefit of this was in its simplicity; only one 
table is needed, and to assign a group to a course is much simpler as users themselves don't need associations with each 
course. We found, however, that this required a lot of complicated logic when getting data for each user. It also made it 
difficult to find which posts a user has not completed. Ultimately, we decided to use 3 separate tables: user_courses, 
user_posts, and user_modules. The tradeoff to this method is it requires more logic when first assigning groups, but makes it much faster to retrieve the necessary data down the line. It also allowed us to add fields like 
'completed_at' and 'updated at' to maintain consistency. In this way, it was much simpler to find what's directly 
associated with each user, rather than always having to deal with one large table. In the end we decided the 'multiple 
tables' model was easier to implement. To represent module reuse across courses, we used a 'course_module' table to keep 
track of the modules within each course while representing and enforcing their ordering, modeled after the existing 
'course_groups' table. This allowed us to assign modules to multiple courses in a way that was consistent and without 
causing any problems.
