# FileRecovery

This is a group project done for a Digital Forensics Course. It's a python script that takes in a .dd disk image as an argument, locates file signatures, and properly recover user generated files without corruption, and then generate a SHA-256 hash for each file recovered. It outputs the file name, the start offset, the end offset, the SHA-256, and then recovers the file to the directory.

## Technologies Used

Python

## How to Run

1. Clone the repo.
2. Add a .dd file to the directory. You can download an example .dd file here – [Link](https://drive.google.com/file/d/1zsl0U4xo9W_0awVfSS01kXCPyrbjK1sx/view?usp=sharing).
3. Run the command `python filerecovery.py <insertdiskimagenamehere>.dd`. Please use python and not python3.
4. This may take a couple minutes to run.

## File Types Supported

- MPG
- PDF
- BMP
- GIF
- ZIP
- JPG
- DOCX
- AVI
- PNG
