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
