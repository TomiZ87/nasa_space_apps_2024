import openai
from bs4 import BeautifulSoup
import time
import json

# Read OpenAI API key from local config.json file
with open('config.json') as config_file:
    config = json.load(config_file)
    openai_api_key = config['API_KEY']

openai.api_key = openai_api_key

def read_filepath():
    filepath = input("Enter the path of your file below:\n")
    return filepath

def parse_osd_file(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    desired_data = dict()

    for line in lines:
        line = line.strip().split("	")
        # The first element in each line will be a key and the value inside of it

        desired_keys = ["Study Identifier", "Study Title", "Study Description", "Study Protocol Description"]    

        
        if len(line) >= 2:
            if line[0] in desired_keys:
                desired_data.update({line[0]: line[1]})
                
    return desired_data

# Create prompt for ChatGPT to create structured experiment information based on "Study Description" and "Study Protocol Description"
def generate_study_summary(input_data):
    study_description = input_data["Study Description"]
    study_protocol_description = input_data["Study Protocol Description"]

    PROMPT = f"""
Based on this document:\n
'{study_description}\n
{study_protocol_description}'

Filter out the following information. There should be 3 - 4 lines of text for each subtopic:

1) The purpose of the study provided in one umbrella sentence

2) The 3-5 most important steps of the conducted experiment to understand the design of the study. Provide the following information about the experiment design step by step: 
2.1. Preperation: Really brief overview (do only include information that is necessary to understand the experiment)
2.2. Sample: Overview about the sample groups and on what criteria the groups are divided
2.3. - 2.4. Further investigation: Summary of general steps that were done to get the final data. You can summarize it in one step or in two separate steps depending on the amount of things that has been done to the sample after the treatment. Try to break that down as short and easy as possible.

3) The content of the final dataset in one umbrella sentence
Note: The output should be understandable for someone without research experience or prior knowledge. Therefore, please leave out all details that are not necessary to understand the course of the experiment (e.g. names of machines being used)

"""
    print("Waiting for response...")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes the input text while exactly sticking to the wanted output structure."},
            {
                "role": "user",
                "content": PROMPT 
            }
        ]
    )
    return response.choices[0].message.content

def generate_poster_html(summarized_information, meta_information):
    HTML_TEMPLATE = f"""
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poster Template</title>
    <link rel="stylesheet" href="template.css">
</head>
<body>
        <!-- Poster Container -->
        <div class="poster-container">

            <!-- Poster Title and Subtitle -->
            <header class="poster-header">
                <h1>{meta_information["Study Title"]}</h1>
            </header>
            <div class="content-section">
                <div class="poster-section" id="purpose-section">
                    <h3>1. Purpose</h3>
                    <div class="content-box">
                        <p></p>
                        <img id="img-placeholder1" class="img-placeholder" src="" alt="image-placeholder">
                    </div>
                </div>
                <div class="poster-section" id="study-design-section">
                    <h3>2. Study Design</h3>
                    <div class="sub-section"><h4>2.1 Preparation</h4></div>
                    <p></p>
                    <img id="img-placeholder2" class="img-placeholder" src="" alt="image-placeholder">
                    <div class="sub-section"><h4>2.2 Treatment</h4></div>
                    <p></p>
                    <img id="img-placeholder3" class="img-placeholder" src="" alt="image-placeholder">
                    <div class="sub-section"><h4>2.3 More</h4></div>
                    <p></p>
                    <img id="img-placeholder4" class="img-placeholder" src="" alt="image-placeholder">
                    <div class="sub-section"><h4>2.4 More</h4></div>
                    <p></p>
                    <img id="img-placeholder5" class="img-placeholder" src="" alt="image-placeholder">
                </div>
                <div class="poster-section" id="dataset-section">
                    <h3>3. Dataset</h3>
                    <p></p>
                    <img id="img-placeholder6" class="img-placeholder" src="" alt="image-placeholder">
                </div>


            </div>
            <div class="meta-information">
                <p>Author: </p>
                <p>DOI: </p>
                <p>[more metadata]</p>
            </div>
        </div>

    
</body>
</html>
"""
    PROMPT = f"""
Use this HTML template:
{HTML_TEMPLATE}

Now generate and include code for the section of class "poster-section" based on the information from this text. Rename the title of subsection "More" matching the content of its text. Only return the html code for the whole page.

Text (just copy the information to the right sub-section):
{summarized_information}

"""

    print("Waiting for response...")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a coding assistant that is tasked to map the summarized information to the given HTML template."},
            {
                "role": "user",
                "content": PROMPT 
            }
        ]
    )

    poster_html = response.choices[0].message.content

    return poster_html

def create_html_file(poster_html):
    with open("website_poster/poster.html", "w") as file:
        file.write(poster_html)

def get_paragraph_text(html_file):
    soup = BeautifulSoup(html_file, "html.parser")
    content_section = soup.find("div", class_="content-section")
    paragraphs = [p.text for p in content_section.find_all("p")]
    return paragraphs

def generate_section_images(section_texts):
    image_urls = []
    
    for i in section_texts:
        print("Generate image for: ", i)
        PROMPT = f"""
Create a minimalistic pictogram-like image that visualize the information of {i} for astronauts who need to 
understand the science behind it.
"""
        response = openai.images.generate(
            model="dall-e-3",
            prompt=PROMPT,
            size="1024x1024",
        )
        image_urls.append(str(response.data[0].url))
        print("Process image.")
        time.sleep(2)
        
    return image_urls

def main():
    #filepath = read_filepath()
    parsed_metadata = parse_osd_file("i_Investigation.txt")
    summary = generate_study_summary(parsed_metadata)
    
    poster_html = (generate_poster_html(summary, parsed_metadata)).replace("```", "")
    
    
    
    image_urls = generate_section_images(get_paragraph_text(poster_html))
    print(len(image_urls))
    for i in range(len(image_urls)):
        
        print(image_urls[i])
        poster_html = poster_html.replace(f'<img id="img-placeholder{i+1}" class="img-placeholder" src="" alt="image-placeholder">', f'<img class="img-placeholder" src="{image_urls[i]}" alt="image-placeholder">')
    create_html_file(poster_html)

    


if __name__ == "__main__":
    main()