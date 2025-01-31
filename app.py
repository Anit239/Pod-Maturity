from flask import Flask, request, render_template, send_from_directory
import cv2
import json
import os

app = Flask(__name__)

def draw_cross(image, cx, cy, size, color):
    cv2.line(image, (cx - size, cy - size), (cx + size, cy + size), color, 2)
    cv2.line(image, (cx - size, cy + size), (cx + size, cy - size), color, 2)

@app.route("/", methods=["GET", "POST"])
def process_image():
    if request.method == "POST":
        try:
            # Handle the uploaded image here
            uploaded_image = request.files["image"]

            # Save the uploaded image to a temporary location
            image_path = "temp_image.jpg"
            uploaded_image.save(image_path)

            # Load your JSON data
            json_file_path = 'A3.json'
            with open(json_file_path, 'r') as json_file:
                annotations_data = json.load(json_file)

            # Process the image
            image = cv2.imread(image_path)

            if image is not None:
                scale_percent = 25
                width = int(image.shape[1] * scale_percent / 100)
                height = int(image.shape[0] * scale_percent / 100)
                image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

                identified_objects = 0

                for image_key, annotation in annotations_data.items():
                    for region in annotation['regions']:
                        shape_attributes = region['shape_attributes']
                        region_attributes = region['region_attributes']

                        if shape_attributes['name'] == 'circle' and identified_objects < 1:
                            cx = shape_attributes['cx']
                            cy = shape_attributes['cy']
                            maturity_status = region_attributes['Matured']

                            cross_size = 10
                            draw_cross(image, int(cx), int(cy), cross_size, (0, 0, 255))  # Change color to red (BGR format)

                            cv2.putText(image, maturity_status, (int(cx) - 10, int(cy) - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Change color to red (BGR format)

                            if (cy - cross_size >= 0) and (cy + cross_size < height) and \
                                    (cx - cross_size >= 0) and (cx + cross_size < width):
                                cardamom_region = image[cy - cross_size:cy + cross_size, cx - cross_size:cx + cross_size]

                            identified_objects += 1

                # Save the processed image
                processed_image_path = "static/processed_image.jpg"
                cv2.imwrite(processed_image_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])

                # Remove the temporary image file
                os.remove(image_path)

                return render_template("result.html", processed_image="processed_image.jpg")
            else:
                return "Failed to load the uploaded image."

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)