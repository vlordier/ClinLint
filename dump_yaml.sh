#!/bin/bash

# Définir le répertoire de départ
REPERTOIRE_DEPART=".vale"

# Définir le fichier de sortie
FICHIER_SORTIE="dump_yml.txt"

# Vider le fichier de sortie s'il existe déjà
> "$FICHIER_SORTIE"

# Trouver tous les fichiers .yml et les traiter
find "$REPERTOIRE_DEPART" -type f -name "*.yml" | while IFS= read -r fichier; do
    echo "Path of Vale rule : $fichier" >> "$FICHIER_SORTIE"
    echo "Content :" >> "$FICHIER_SORTIE"
    cat "$fichier" >> "$FICHIER_SORTIE"
    echo -e "\n---\n" >> "$FICHIER_SORTIE"
done

echo "Dump terminé. Les données sont enregistrées dans $FICHIER_SORTIE."
