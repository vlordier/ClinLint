# API Endpoints

## `/suggestions`

- **Method**: POST
- **Description**: Generates Vale linting issues and LLM suggestions for a single text.
- **Request**:
  ```json
  {
      "text": "The patient was observed to have a significant improvement.",
      "vale_config": "config/rules/final-template.ini",
      "llm_template": "improvement_prompt"
  }
  ```
- **Response**:
  ```json
  {
      "vale_issues": { ... },
      "suggestions": "Replace 'significant' with a specific term."
  }
  ```

## `/suggestions/batch`

- **Method**: POST
- **Description**: Processes multiple texts and generates suggestions for each.
- **Request**:
  ```json
  {
      "texts": [
          {
              "text": "The patient was observed to have a significant improvement.",
              "vale_config": "config/rules/final-template.ini",
              "llm_template": "improvement_prompt"
          }
      ]
  }
  ```
- **Response**:
  ```json
  {
      "results": [
          {
              "vale_issues": { ... },
              "suggestions": "Replace 'significant' with a specific term."
          }
      ]
  }
  ```
```
