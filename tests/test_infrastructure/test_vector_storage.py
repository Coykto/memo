# import pytest
# from src.infrastructure.vector_db.pinecone_vector_storage import PineconeVectorStorage
#
#
# @pytest.mark.asyncio
# async def test_pinecone_store_vector():
#     with patch('pinecone.Pinecone') as mock_pinecone:
#         storage = PineconeVectorStorage(api_key="test-key", host="test-host")
#
#         await storage.store_vector(
#             vector=[0.1, 0.2, 0.3],
#             memo_id="test-id",
#             metadata={"user_id": "test-user"}
#         )
#
#         mock_pinecone.return_value.Index.return_value.upsert.assert_called_once()
#
#
# @pytest.mark.asyncio
# async def test_pinecone_search():
#     with patch('pinecone.Pinecone') as mock_pinecone:
#         mock_pinecone.return_value.Index.return_value.query.return_value = \
#             MagicMock(matches=[
#                 MagicMock(
#                     id="test-id",
#                     score=0.95,
#                     metadata={"user_id": "test-user"}
#                 )
#             ])
#
#         storage = PineconeVectorStorage(api_key="test-key", host="test-host")
#         results = await storage.search(
#             query_vector=[0.1, 0.2, 0.3],
#             user_id="test-user",
#             limit=10
#         )
#
#         assert len(results) == 1
#         assert results[0]["id"] == "test-id"
#         assert results[0]["score"] == 0.95
