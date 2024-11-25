import json
import os
import uuid
from urllib.parse import urlparse, parse_qs
from neo4j import GraphDatabase
import ollama
from datetime import datetime

from app.llm.embeddings.ollama_embeddings import embed


class InteractionService:
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j+s://0fe3408d.databases.neo4j.io", auth=("neo4j", os.getenv('GRAPHDB_PASS')))
        self.verify_connectivity()

    def verify_connectivity(self):
        print("Neo4j health check", self.driver.verify_connectivity())

    def parse_url(self, url):
        parsed = urlparse(url)
        search_path = parsed.path
        return parsed.hostname, search_path

    def generate_embedding(self, text):
        return embed.embed_query(text)

    def store_interaction(self, interactions):
        if not interactions:
            return
        print(interactions)
        previous_node_id, prev_edge = None, None
        interaction_id = interactions[0]['interactionId']
        with self.driver.session() as session:
            # Find the latest node with the same interactionId (if exists) to create an edge to the new batch's first node
            last_interaction_node = session.run("""
                MATCH (n:InteractionNode {interaction_id: $interaction_id})
                RETURN n ORDER BY n.timestamp DESC LIMIT 1
            """, interaction_id=interaction_id).single()

            # Initialize previous node to link interactions sequentially
            previous_node_id = last_interaction_node["n"]["unique_id"] if last_interaction_node else None
            prev_edge = last_interaction_node["n"]["event_type"] if last_interaction_node else None

            print("Previous node found, ", previous_node_id)
        for interaction_data in interactions:
            interaction_id = interaction_data.get('interactionId', str(uuid.uuid4()))
            hostname, search_path = self.parse_url(interaction_data.get('pageURL'))
            event_type = interaction_data['eventType']
            element_id = interaction_data.get('selector')
            description = interaction_data.get('description')
            data = interaction_data.get('data')
            nearestText = interaction_data.get('nearestText')
            xpath = interaction_data.get('xpath')
            timestamp = interaction_data.get('timestamp')

            embed_text = description
            if data:
                embed_text += f" The element has data of {data}."
            if nearestText:
                embed_text += f" The interaction happenend around the elements with data of {nearestText}."


            # Generate embedding using Ollama Llama3.1
            embedding = self.generate_embedding(embed_text)

            previous_node_id = self.store_interaction_data(
                interaction_id=interaction_id,
                hostname=hostname,
                search_path=search_path,
                event_type=event_type,
                element_id=element_id,
                description=description,
                embedding=embedding,
                data = data,
                nearest_text = nearestText,
                xpath = xpath,
                timestamp = timestamp,
                previous_node_id = previous_node_id,
                prev_edge = prev_edge
            )
        return True

    def store_interaction_data(self, interaction_id, hostname, search_path, event_type, element_id, description, embedding, data, nearest_text, xpath, timestamp, previous_node_id, prev_edge):
        unique_node_id = f"{hostname}_{search_path}_{element_id}"

        with self.driver.session() as session:
            # Create or update the node with description and embedding
            session.run("""
                MERGE (n:InteractionNode {unique_id: $unique_node_id})
                ON CREATE SET n.hostname = $hostname,
                              n.search_path = $search_path,
                              n.interaction_id = $interaction_id,
                              n.event_type = $event_type,
                              n.element_id = $element_id,
                              n.description = $description,
                              n.embedding = $embedding,
                              n.data = $data,
                              n.nearest_text = $nearest_text,
                              n.xpath = $xpath,
                              n.timestamp= datetime($timestamp),
                              n.update_count = 1
                ON MATCH SET n.description = n.description + " | " + $description,
                             n.event_type = $event_type,
                             n.embedding = $embedding,  
                             n.data = $data,
                             n.nearest_text = $nearest_text,
                             n.xpath = $xpath,
                             n.timestamp= datetime($timestamp),
                             n.update_count = n.update_count + 1
            """, unique_node_id=unique_node_id, hostname=hostname, search_path=search_path, event_type=event_type, interaction_id=interaction_id,
                        element_id=element_id, description=description, embedding=embedding,data = data,
                nearest_text = nearest_text, xpath = xpath, timestamp = timestamp)

            # Link nodes under a common interaction flow
            edge_name = prev_edge.upper() if prev_edge else "START"
            if previous_node_id:
                session.run(f"""
                                MATCH (prev:InteractionNode {{unique_id: $previous_node_id}})
                                MATCH (curr:InteractionNode {{unique_id: $unique_node_id}})
                                MERGE (prev)-[:{edge_name} {{timestamp: datetime($timestamp_str)}}]->(curr)
                            """, previous_node_id=previous_node_id, unique_node_id=unique_node_id,
                            timestamp_str=timestamp)
        print("Node saved, ", unique_node_id)
        return unique_node_id
