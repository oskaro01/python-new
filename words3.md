tell me how do i run things







1:42 AM






To run the Chat Lab:
cd C:\Users\ASUS\Desktop\python-new\my_python_work\web_practice\04_chat_lab
Create the model migration once:
..\..\..\.venv\Scripts\python.exe manage.py makemigrations chat
..\..\..\.venv\Scripts\python.exe manage.py migrate
Create a login user:
..\..\..\.venv\Scripts\python.exe manage.py createsuperuser
Start the server on port 8003:
..\..\..\.venv\Scripts\python.exe manage.py runserver 8003
Open:
http://127.0.0.1:8003/
Useful pages:
http://127.0.0.1:8003/
http://127.0.0.1:8003/chat/
http://127.0.0.1:8003/admin/
Stop the server with:
CTRL + C
For the next lessons, you only need to start the server when you want to view the UI.

====
..\\..\\..\\.venv\\Scripts\\python.exe manage.py migrate

cd C:\Users\ASUS\Desktop\python-new\my_python_work\web_practice\04_chat_lab
..\..\..\.venv\Scripts\python.exe manage.py runserver 8003
====
$env:CHAT_MESSAGE_TTL_SECONDS = "60"
echo $env:CHAT_MESSAGE_TTL_SECONDS
Remove-Item Env:CHAT_MESSAGE_TTL_SECONDS 
or
Remove-Item Env:CHAT_MESSAGE_TTL_SECONDS -ErrorAction SilentlyContinue
===
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py runserver 8003    [if you in path >> PS C:\Users\ASUS\Desktop\python-new>]

.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py migrate
===