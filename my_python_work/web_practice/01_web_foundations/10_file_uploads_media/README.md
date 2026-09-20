# Lesson 10: File Uploads And Media

Most real web apps eventually need uploaded files:

- product images
- profile pictures
- receipts
- PDFs
- CSV imports

This lesson shows the basic idea without Django yet.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/10_file_uploads_media/app.py
```

Open the URL printed in the terminal.

## What This Teaches

- File upload forms need `enctype="multipart/form-data"`.
- Uploaded files are bytes, not normal text input.
- The server reads the request body.
- User-provided file names should not be trusted directly.
- Uploaded files should go into a controlled folder.
- Apps usually limit file size and allowed extensions.

## Try Uploading

Good small test files:

```text
notes.txt
budget.csv
picture.png
receipt.pdf
```

The app saves files into:

```text
my_python_work/web_practice/01_web_foundations/10_file_uploads_media/uploads/
```

That folder is ignored by Git because uploaded files are generated practice output.

## Key Memory Hook

```text
Normal form = text fields
Upload form = text fields + file bytes
```

## Django Preview

Later Django will make this easier with:

- `FileField`
- `ImageField`
- `request.FILES`
- `MEDIA_ROOT`
- `MEDIA_URL`

