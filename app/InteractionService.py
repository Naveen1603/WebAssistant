import json
import os
import uuid
from urllib.parse import urlparse, parse_qs
from neo4j import GraphDatabase


class InteractionService:
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j+s://0fe3408d.databases.neo4j.io", auth=("neo4j", os.getenv('GRAPHDB_PASS')))

    def process_interactions(self, interactions):
        with self.driver.session() as session:
            for interaction in interactions:
                interaction_id = interaction['interactionId']  # Generate a unique ID for the interaction

                # Capture the full page URL including both path and query parameters
                page_url = interaction['pageURL']

                # Parse the URL to segregate path and query parameters
                parsed_url = urlparse(page_url)
                path = parsed_url.path
                query_params = parse_qs(parsed_url.query)

                # Other interaction attributes
                event_type = interaction['eventType']
                element_id = interaction.get('elementId', '')
                element_class = interaction.get('elementClass', '')
                element_text = interaction.get('elementText', '')
                description = interaction.get('description', '')
                selector = interaction.get('selector', '')
                xpath = interaction.get('xpath', '')

                # Create or match the Page node based on the path
                session.run("""
                    MERGE (p:Page {url: $url, path: $path})
                    """, url=page_url, path=path)

                # Create the Interaction node and the relationship
                session.run("""
                    MATCH (p:Page {url: $url})
                    CREATE (i:Interaction {id: $interaction_id, eventType: $event_type, 
                                           elementId: $element_id, elementClass: $element_class, 
                                           elementText: $element_text, description: $description, 
                                           selector: $selector, xpath: $xpath})
                    CREATE (p)-[:ACTION {type: $event_type}]->(i)
                    """,
                            url=page_url,
                            path=path,
                            interaction_id=interaction_id,
                            event_type=event_type,
                            element_id=element_id,
                            element_class=element_class,
                            element_text=element_text,
                            description=description,
                            selector=selector,
                            xpath=xpath
                            )

        return json.dumps({"status": "success", "message": "Interaction recorded"}), 200
