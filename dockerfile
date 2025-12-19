
FROM hashicorp/terraform:latest


WORKDIR /app


COPY . .

# Commande par défaut
ENTRYPOINT ["terraform"]