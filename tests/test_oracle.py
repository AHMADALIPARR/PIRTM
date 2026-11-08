"""Unit tests for PIRTM Content-Addressed Storage and Embedding Oracle."""

import unittest
from pirtm.oracle.cas import ContentAddressedStore, compute_sha256
from pirtm.oracle.retrieval import EmbeddingOracle


class TestCASAndOracle(unittest.TestCase):
    def setUp(self):
        self.cas = ContentAddressedStore()
        self.oracle = EmbeddingOracle(cas=self.cas)

    def test_cas_put_get_immutability(self):
        data = "test invariant I04 immutability content"
        sha = self.cas.put(data, creator="A01", created_at_utc="2026-10-10T00:00:00Z")
        self.assertEqual(sha, compute_sha256(data))

        retrieved = self.cas.get(sha)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.decode("utf-8"), data)

        # Immutability: re-putting same content succeeds
        sha2 = self.cas.put(data, creator="A01", created_at_utc="2026-10-10T00:00:00Z")
        self.assertEqual(sha, sha2)

        # Provenance verification
        prov = self.cas.get_provenance(sha)
        self.assertIsNotNone(prov)
        self.assertEqual(prov.creator, "A01")

        ver = self.cas.verify(sha)
        self.assertTrue(ver["integrity_valid"])
        self.assertTrue(ver["has_provenance"])

    def test_oracle_embed_deterministic_fallback(self):
        doc1 = "quantum circuit unitarity invariant"
        doc2 = "historical nostalgic quatrain evaluation"
        vec1 = self.oracle.embed(doc1)
        vec2 = self.oracle.embed(doc2)
        self.assertEqual(len(vec1), 64)
        self.assertEqual(len(vec2), 64)
        # Fallback should be deterministic
        self.assertEqual(vec1, self.oracle.embed(doc1))
        self.assertNotEqual(vec1, vec2)

    def test_oracle_retrieve_and_filter(self):
        sha1 = self.oracle.record_document(
            content="unitary transformation matrix Pauli gate",
            creator="A04",
            created_at_utc="2026-10-10T00:00:00Z",
            metadata={"domain": "quantum", "tag": "unitary"},
        )
        sha2 = self.oracle.record_document(
            content="causal DAG event order partial order",
            creator="A01",
            created_at_utc="2026-10-10T00:00:00Z",
            metadata={"domain": "causality", "tag": "dag"},
        )

        results = self.oracle.retrieve("unitary transformation", limit=5)
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0].identifier, sha1)

        # Retrieval with filter
        filtered = self.oracle.retrieve("transformation", limit=5, filters={"domain": "causality"})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].identifier, sha2)


if __name__ == "__main__":
    unittest.main()
