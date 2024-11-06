#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal: $meal ($cuisine, $price, $difficulty)"
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1
  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1
  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve meal."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve meal by name."
    exit 1
  fi
}

clear_catalog() {
  echo "Clearing meal catalog..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal catalog cleared."
  else
    echo "Failed to clear catalog."
    exit 1
  fi
}

############################################################
#
# Battle Management
#
############################################################

prep_combatant() {
  meal_name=$1
  echo "Preparing meal as combatant: $meal_name"
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "{\"meal\":\"$meal_name\"}")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Combatant prepared successfully."
  else
    echo "Failed to prepare combatant."
    exit 1
  fi
}

battle() {
  echo "Initiating battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Battle completed successfully."
  else
    echo "Failed to initiate battle."
    exit 1
  fi
}

get_combatants() {
  echo "Getting all combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve combatants."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing all combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

get_leaderboard() {
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  echo "$response" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}

############################################################
#
# Run Test Sequence
#
############################################################

# Perform health checks
check_health
check_db

# Create meals and prepare combatants for battle
create_meal "Spaghetti" "Italian" 12.99 "MED"
create_meal "Taco" "Mexican" 5.99 "LOW"
create_meal "Sushi" "Japanese" 15.49 "HIGH"
get_meal_by_name "Spaghetti"
get_meal_by_id 1
prep_combatant "Spaghetti"
prep_combatant "Taco"
get_combatants
battle
get_leaderboard
delete_meal 1
clear_catalog
clear_combatants

echo "All tests passed successfully!"

