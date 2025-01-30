# This is a command line program acting as the central web server for your moderation management.


# Imports
import argparse
import time
from Process_Logs import process_logs, package_text_data, get_author, get_log_time, get_utc_offset

def verify_files_allowed(filename):
    allowed_filenames = {".txt",".log"}
    if any(filename.endswith(file_ext) for file_ext in allowed_filenames):
        return True
    else:
        return False

def initialize_server():
    """
    :inputs: none
    :return: launch_args,
    """
    global last_upload_time
    last_upload_time = time.time()
    parser = argparse.ArgumentParser(
        prog='VRC_Moderation_Server',
        description='Processes logs for VRChat',
        epilog='Put some helpful words here later')

    #parser.add_argument("filename", "-f")
    parser.add_argument("-da", "--database", default="logs_database.db")
    parser.add_argument("-de", "--debug", action="store_true")
    parser.add_argument("-uf", "--uploadfolder", default="TempLogs")
    parser.add_argument("-df", "--datafolder", default="OrganizedLogs")
    parser.add_argument("-mf", "--maxfilesizemb", default=10, type=int)# max filesize in MB
    parser.add_argument("-mu", "--maxuploads", default=5, type=int)# max uploads in a single batch
    parser.add_argument("-rl", "--ratelimit", default=1, type=int)# max requests per second

    args = parser.parse_args()
    #print(args.database, args.debug)
    return args

def verify_non_abuse(files, max_file_size, max_uploads, rate_limit):
    global last_upload_time
    current_time = time.time()

    if len(files) > max_uploads:
        return False, f"Too many files." #. Maximum {max_uploads} files allowed."

    if current_time - last_upload_time < rate_limit:
        return False, f"Upload rate limit exceeded. Try again later."

    for file in files:
        if file.content_length and file.content_length > max_file_size * 1024 * 1024:
            return False, f"File {file.filename} exceeds the {max_file_size} MB limit."

    last_upload_time = current_time  # Update last upload time
    return True, None


def start_server(launch_args):
    """
    Starts server
    """
    # Configuration variables
    from flask import Flask, render_template, jsonify, request
    from werkzeug.utils import secure_filename
    from os import makedirs, path, listdir
    from shutil import move
    app = Flask(__name__)

    app.config['UPLOAD_FOLDER'] = launch_args.uploadfolder
    app.config['DATA_FOLDER'] = launch_args.datafolder
    makedirs(launch_args.uploadfolder, exist_ok=True) # Makes the upload folder if it doesn't exist.

    # Browser functions
    @app.route('/')
    def upload_form():
        return render_template('upload_logs.html')

    @app.route('/transfer_logs', methods=['POST'])
    def transfer_logs():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('file')
        if not files:
            return jsonify({'error': 'No selected files'}), 400

        # Validate against abuse
        is_valid, error_message = verify_non_abuse(files, launch_args.maxfilesizemb, launch_args.maxuploads,
                                                   launch_args.ratelimit)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        saved_files = []
        for file in files:
            if file.filename == '':
                continue
            if file and verify_files_allowed(file.filename):
                filename = secure_filename(file.filename)
                file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)


        for filename in listdir(app.config['UPLOAD_FOLDER']): # For each file, we're going to move to correct user folder.
            source_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            text_file_data  = package_text_data(source_path)
            username, userid = get_author(text_file_data)
            dest_path = path.join(app.config['DATA_FOLDER'], userid, filename)
            makedirs(path.join(app.config['DATA_FOLDER'], userid), exist_ok=True)
            move(source_path , dest_path)
            #time_created, time_modified, filename_timestamp, text_file_data_timestamp = get_log_time(text_file_data, filename)
            #utc_offset = get_utc_offset(time_created, filename_timestamp)
        if saved_files:
            return jsonify({'success': f'Files uploaded: {", ".join(saved_files)}'}), 200
        return jsonify({'error': 'No valid files uploaded'}), 400

    # Starts server.
    app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == "__main__":
    launch_args = initialize_server()
    start_server(launch_args)