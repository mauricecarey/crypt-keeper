docker-containers:
  lookup:
    postgres:
      image: "postgres:9.4"
      runoptions:
        - "-p 5432:5432"
        - "-e POSTGRES_USER=ck"
        - "-e POSTGRES_DB=ck"
        - "-e POSTGRES_PASSWORD=Passw0rd"
    redis:
      image: "redis:3"
      runoptions:
        - "-p 6379:6379"
    
