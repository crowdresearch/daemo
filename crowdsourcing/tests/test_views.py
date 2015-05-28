from django.test import TestCase
import unittest

# Create your tests here.
import unittest

class BaseTestCase(unittest.TestCase):
    def testBasic(self):
    	self.assertEqual(True, True) # better be
        self.assertEqual(1+1, 2) 
        