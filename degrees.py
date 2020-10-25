import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def clean_neighbors(uncleanedNeighbors, targetToRemoveId):
    """ Removes the current node from the list of actors who starred in a movie """

    for neighbor in uncleanedNeighbors:
        if neighbor[1] == targetToRemoveId:
            uncleanedNeighbors.remove(neighbor)
            return uncleanedNeighbors


def find_and_reverse_shortest_path(node):
    """ Backtrack the path taken back to the source """

    path = list()

    while node.parent is not None:
        path.append((node.state))
        node = node.parent
    
    path.reverse()

    return path


def explored_actors(exploredActors):
    """ Keeps track of the ids of actors who have already been explored """

    personId = list()

    for exploredActor in exploredActors:
        personId.append(exploredActor[1])

    return personId


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Create a frontier object from the QueueFrontier class to hold node objects
    frontier = QueueFrontier()

    # Create a set to keep track of the explored nodes
    exploredActors = set()

    # Create a node object for the source from the Node class
    uncleaned = neighbors_for_person(source) 
    start = Node(state=(None, source), parent=None, action=clean_neighbors(uncleaned, source))

    # Add the source node to the frontier
    frontier.add(start)

    # Traverse the stars until the target is reached
    while True:

        # Make sure the frontier is not empty
        if frontier.empty():
            return None

        # Pop a node from the frontier and then add it to the explored
        node = frontier.remove()
        exploredActors.add(node.state)
        
        neighbors = clean_neighbors(neighbors_for_person(node.state[1]), node.state[1])

        # Pick all the neighbors of the current node that are not in frontier and not explored then add them
        # to the frontier
        for neighbor in neighbors:
            if not frontier.contains_state(neighbor) and neighbor[1] not in explored_actors(exploredActors):
                child = Node(state=neighbor, parent=node, action=neighbors)

                # Check to see if that is the target node and then stop otherwise move on
                if neighbor[1] == target:
                    return find_and_reverse_shortest_path(child)

                frontier.add(child) 

    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
