import unittest
from auth import get_password_hash, verify_password


class Test(unittest.TestCase):

    def setUp(self):
        self.pwd = 'b'
        self.hashed_pwd = ('$2b$12$o5FUxT.lT6PZXU8KHPz4tug1yG'
                           'I.gXuyZNT8VWbKBNaAEP10/yI.W')

    def test_plain_password(self):
        self.assertTrue(verify_password(self.pwd, self.hashed_pwd))


    def test_hashed_password(self):
        hashed_pwd = get_password_hash(self.pwd)
        self.assertTrue(verify_password(self.pwd, hashed_pwd))
        self.assertNotEquals(hashed_pwd, self.hashed_pwd)


unittest.main(verbosity=2)
