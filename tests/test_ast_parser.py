"""
Unit tests for AST and Regex code parsing tool across frameworks.
Syllabus Alignment: Unit 1 & Unit 4 (Code analysis and modeling).
"""

import unittest
from src.tools.ast_parser_tool import ASTParserTool


class TestASTParser(unittest.TestCase):

    def setUp(self):
        self.parser = ASTParserTool()

    def test_fastapi_parsing(self):
        code = """
from fastapi import FastAPI, Depends
app = FastAPI()

def get_token(): return "token"

@app.get("/items/{item_id}", tags=["Items"])
def read_item(item_id: int, q: str = None):
    '''Fetch item by ID.'''
    return {"item_id": item_id, "q": q}

@app.post("/items", status_code=201, tags=["Items"])
def create_item(name: str, auth: str = Depends(get_token)):
    '''Create new item.'''
    return {"name": name}
"""
        endpoints = self.parser.parse(code, framework="fastapi")
        self.assertEqual(len(endpoints), 2)

        ep1 = endpoints[0]
        self.assertEqual(ep1.path, "/items/{item_id}")
        self.assertEqual(ep1.method, "GET")
        self.assertEqual(ep1.summary, "Fetch item by ID.")
        self.assertEqual(len(ep1.parameters), 2)

        ep2 = endpoints[1]
        self.assertEqual(ep2.path, "/items")
        self.assertEqual(ep2.method, "POST")
        self.assertTrue(ep2.auth_required)

    def test_flask_parsing(self):
        code = """
from flask import Flask
app = Flask(__name__)

@app.route("/api/users", methods=["GET"])
def get_users():
    return []

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    return {}
"""
        endpoints = self.parser.parse(code, framework="flask")
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0].method, "GET")
        self.assertEqual(endpoints[1].method, "PUT")

    def test_express_parsing(self):
        code = """
const express = require('express');
const router = express.Router();

router.get('/orders/:orderId', authenticate, (req, res) => {
    res.json({ id: req.params.orderId });
});

router.post('/orders', (req, res) => {
    res.status(201).json({ created: true });
});
"""
        endpoints = self.parser.parse(code, framework="express")
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0].path, "/orders/{orderId}")
        self.assertEqual(endpoints[0].method, "GET")
        self.assertTrue(endpoints[0].auth_required)


if __name__ == "__main__":
    unittest.main()
