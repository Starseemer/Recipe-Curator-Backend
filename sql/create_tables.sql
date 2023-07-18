DROP TABLE IF EXISTS "users" CASCADE;
DROP TABLE IF EXISTS "recipes" CASCADE;
DROP TABLE IF EXISTS "recipes_users" CASCADE;
DROP TABLE IF EXISTS "comments" CASCADE;
DROP TABLE IF EXISTS "shared_voc" CASCADE;
DROP TABLE IF EXISTS "recipes_to_users" CASCADE;
DROP TABLE IF EXISTS "shared_voc_to_recipes" CASCADE;



CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "email" text UNIQUE NOT NULL,
  "sha256_password" text,
  "name" text,
  "surname" text,
  "user_session_token" text,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar UNIQUE NOT NULL,
  "description" text,
  "instructions" text,
  "cooking_time" float,
  "user_id" integer,
  "serving_size" integer,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "shared_voc" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar UNIQUE NOT NULL,
  "desc" text,
  "type" varchar NOT NULL,
  "user_id" integer NOT NULL
);

CREATE TABLE "comments" (
  "id" SERIAL PRIMARY KEY,
  "user_email" text NOT NULL,
  "body" text,
  "shared_voc_id" integer NOT NULL
);

CREATE TABLE "recipes_to_users" (
  "recipes_id" integer,
  "users_id" integer,
  PRIMARY KEY ("recipes_id", "users_id")
);

CREATE TABLE "shared_voc_to_recipes" (
  "shared_voc_id" integer,
  "recipes_id" integer,
  PRIMARY KEY ("shared_voc_id", "recipes_id")
);

COMMENT ON COLUMN "recipes"."description" IS 'Description of the recipe';

COMMENT ON COLUMN "recipes"."instructions" IS 'Detailed instruction of how to cook';

ALTER TABLE "recipes" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "recipes_to_users" ADD FOREIGN KEY ("recipes_id") REFERENCES "recipes" ("id");

ALTER TABLE "recipes_to_users" ADD FOREIGN KEY ("users_id") REFERENCES "users" ("id");

ALTER TABLE "comments" ADD FOREIGN KEY ("user_email") REFERENCES "users" ("email");

ALTER TABLE "comments" ADD FOREIGN KEY ("shared_voc_id") REFERENCES "shared_voc" ("id");

ALTER TABLE "shared_voc" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "shared_voc_to_recipes" ADD FOREIGN KEY ("shared_voc_id") REFERENCES "shared_voc" ("id");

ALTER TABLE "shared_voc_to_recipes" ADD FOREIGN KEY ("recipes_id") REFERENCES "recipes" ("id");

