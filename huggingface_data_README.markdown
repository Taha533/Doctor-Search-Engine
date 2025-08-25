# Bangladesh Doctors Dataset

## Dataset Description

The **Bangladesh Doctors Dataset** contains information about 5,362 doctors across Bangladesh, scraped from [Doctor Bangladesh](https://www.doctorbangladesh.com/). The dataset is provided in two formats: raw (`raw_data.json`) and cleaned (`cleaned_data.json`). It was created to support a Retrieval-Augmented Generation (RAG) system for querying doctor information by specialty and location, such as "List doctors in Dhaka" or "Suggest Dermatologists in Jessore." This dataset is useful for healthcare applications, natural language processing, and data analysis in the medical domain.

### Dataset Summary
- **Source**: [Doctor Bangladesh](https://www.doctorbangladesh.com/)
- **Records**: 5,362 doctor profiles
- **Files**:
  - `raw_data.json`: Raw scraped data with URLs, titles, and page content.
  - `cleaned_data.json`: Filtered data with doctor names, specialties, locations, and URLs.
- **License**: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike)
- **Intended Use**: Research, healthcare applications, NLP tasks (e.g., RAG systems, chatbots).

## Dataset Structure

### `raw_data.json`
- **Description**: Contains raw data scraped from doctor profile pages and other sections of the website.
- **Fields**:
  - `url` (string): URL of the page (e.g., `https://www.doctorbangladesh.com/dr-md-shaukat-haidar/`).
  - `title` (string): Page title, often including doctor name, specialty, and location (e.g., "Dr. Md. Shaukat Haidar - Dermatologist in Jessore").
  - `content` (string): Raw text content of the page, including doctor details, hospital information, or other text.
- **Size**: ~5,362 records (varies based on scraping scope).
- **Example**:
  ```json
  {
    "url": "https://www.doctorbangladesh.com/dr-md-shaukat-haidar/",
    "title": "Dr. Md. Shaukat Haidar - Dermatologist in Jessore",
    "content": "Dr. Md. Shaukat Haidar\nSpecialty: Dermatologist\nLocation: Jessore\n..."
  }
  ```

### `cleaned_data.json`
- **Description**: Filtered and processed data, focusing on doctor profiles with structured fields extracted from `raw_data.json`.
- **Fields**:
  - `url` (string): Doctor’s profile URL.
  - `title` (string): Doctor’s name (e.g., "Dr. Md. Shaukat Haidar").
  - `specialty` (string): Medical specialty (e.g., "Dermatologist", "Dentist", "Child Specialist").
  - `location` (string): Practice location (e.g., "Jessore", "Dhaka", "Chittagong").
- **Size**: 5,362 records (filtered to include only URLs starting with `https://www.doctorbangladesh.com/dr-`).
- **Example**:
  ```json
  {
    "url": "https://www.doctorbangladesh.com/dr-md-shaukat-haidar/",
    "title": "Dr. Md. Shaukat Haidar",
    "specialty": "Dermatologist",
    "location": "Jessore"
  }
  ```

## Data Collection

- **Source**: Scraped from [Doctor Bangladesh](https://www.doctorbangladesh.com/) using a Scrapy crawler.
- **Method**: The crawler targeted doctor profile pages (URLs starting with `/dr-`), hospital pages, and specialty/location listings. Data was extracted from HTML content, including titles and text.
- **Date**: Collected as of August 2025.

## Usage

This dataset can be used for:
- **Healthcare Applications**: Build search engines or chatbots to find doctors by specialty or location.
- **NLP Tasks**: Train or evaluate RAG systems, question-answering models, or information retrieval systems.
- **Data Analysis**: Analyze doctor distribution by specialty or region in Bangladesh.

### Example Code
To load and use the cleaned dataset with Python:
```python
import json

with open('cleaned_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter Dermatologists in Dhaka
dermatologists_dhaka = [d for d in data if d['specialty'] == 'Dermatologist' and d['location'] == 'Dhaka']
for doctor in dermatologists_dhaka:
    print(f"Doctor: {doctor['title']}, URL: {doctor['url']}, Location: {doctor['location']}, Specialty: {doctor['specialty']}")
```

### RAG System Integration
The dataset was used in a Doctor Search Engine project with FAISS and Groq’s LLaMA model. See the [project repository](https://github.com/your-repo/doctor-search-engine) for implementation details, including a Streamlit app.

## Installation

1. **Download the Dataset**:
   - Clone this Hugging Face dataset or download `raw_data.json` and `cleaned_data.json`.
2. **Install Dependencies** (for processing or RAG system):
   ```bash
   pip install pandas json
   ```
   For the full RAG system, install:
   ```bash
   pip install langchain langchain-community langchain-huggingface langchain-groq python-dotenv sentence-transformers faiss-cpu
   ```
3. **Load the Dataset**:
   Use the example code above or integrate with libraries like LangChain for advanced applications.

## Limitations

- **Missing Fields**: The cleaned dataset lacks contact information and hospital details due to inconsistent source data. The raw dataset may contain these in the `content` field but requires further parsing.
- **Data Completeness**: Some doctor profiles may have incomplete or ambiguous specialties/locations due to website formatting variations.
- **Coverage**: Limited to data available on Doctor Bangladesh as of August 2025. May not include all doctors in Bangladesh.
- **Accuracy**: Extracted specialties and locations rely on regex patterns and may have errors if titles deviate from expected formats (e.g., "Dr. Name - Specialty in Location").

## License

This dataset is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**. You may use, share, and adapt the data for non-commercial purposes, provided you give appropriate credit and distribute any adaptations under the same license. See [LICENSE](LICENSE) for details.

## Citation

If you use this dataset in your work, please cite it as:
```
Bangladesh Doctors Dataset, scraped from Doctor Bangladesh (https://www.doctorbangladesh.com/), August 2025. Available on Hugging Face.
```

## Contact

For questions, issues, or contributions, please open an issue on the [Hugging Face dataset page](https://huggingface.co/datasets/your-username/bangladesh-doctors) or contact the dataset creator via [LinkedIn](https://www.linkedin.com/in/your-profile).

## Acknowledgments

- **Doctor Bangladesh**: For providing the source data.
- **Hugging Face**: For hosting the dataset.
- **Groq and LangChain**: For enabling the RAG system used with this dataset.

---

*Created by [Your Name] for the Doctor Search Engine project, August 2025.*
```