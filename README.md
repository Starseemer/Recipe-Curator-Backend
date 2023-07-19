# Recipe-Curator-Backend
This is backend system  allows users to create, store, and share their recipes. One of the critical aspects of the system is to provide a shared vocabulary that can be maintained by users.

## Setup process
1. Run the docker-compose file by
   - ``` docker-compose up --build ```
2. Wait for containers to build
3. Open (pgadmin)[localhost:5050]
4. Create server with the following properties

   - ![This image show pgadmin properties](https://github.com/Starseemer/Recipe-Curator-Backend/blob/main/media/db_server_create_1.png)
   - ![This image show pgadmin properties](https://github.com/Starseemer/Recipe-Curator-Backend/blob/main/media/db_server_create_2.png)

6. When we press save button, pgadmin trigers a automatic script that creates our tables. If not copy the script from [here](https://github.com/Starseemer/Recipe-Curator-Backend/blob/main/sql/create_tables.sql) and paste it to script tool.
7. The end product should look like this

   - ![This image show pgadmin folder structure after running the create tables script run](https://github.com/Starseemer/Recipe-Curator-Backend/blob/main/media/db_server_create_3.png)
9. Your backend is ready to use.

## Usage
There 6 services under the backend system. These are;
1. Auth Service
2. Comments Service
3. Favourites Service
4. Recipe Service
5. Search Service
6. Shared Vocabulary Service

You can find an example usage of each end point of each service under the postman collections directory.

- To be able to use the API you need to create a user from auth-service by calling ``` /signup ``` end-point and setting **_email, password, name, and surname_**
- Then, you need to login to the system by calling /login with email, and password in the body of the POST request
  - This, call is going to return a JSON Web Token which is valid for 48 hours. You need to add this token to each request header with the id of Authorization

## Creating Recipes

- To be able to create recipes, we first need to create a shared vocabulary item. Because, the system designed as you cannot create recipe without at least having an ingridient or cooking term.
- To create a Shared Vocabulary item you need to either call ``` /ingredients ``` or ``` /cooking-terms ``` end-points with a POST request that has **_name, and description_** of the item you are trying to add.
  - The name should be unique, if not system won't allow you to add a new item
- After this, you can create a new recipe by calling the end-point ``` /recipes ``` with a POST request that has **_title, description, instructions, ingridient and cooking terms ids, and optionally, cooking time in minutes and/or serving size_.**
  - The response will be a confirmation message and response code of 201
- Rest of the service is strait forward

