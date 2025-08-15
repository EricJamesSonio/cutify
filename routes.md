Page Routes (HTML Views)
Route Path	Purpose / Page Name	Template File
/	Home page	home/home.html
/choices	Mood selection page	choices/choices.html
/sadpage	Sad mood page	choosen/sad.html
/happypage	Happy mood page	choosen/happy.html
/missingpage	Missing mood page	choosen/missing.html
/angrypage	Angry mood page	choosen/angry.html
/confusedpage	Confused mood page	choosen/confused.html
/hurtpage	Hurt mood page	choosen/hurt.html
/finepage	Fine mood page	choosen/fine.html
/me	Chat/messaging page	me/me.html
/visit	Visit room page	me/visit.html
🔌 API Routes
Route Path	Method	Purpose
/api/chat	POST	Chat endpoint for mood responses
/api/health	GET	Health check for the bot