from django.test import TestCase
import swiftbrowser.views
from swiftbrowser.utils import *


class SplitAclTest(TestCase):

    def setUp(self):

        # Create an empty
        self.expected = {
            "users": [],
            "referrers": [],
            "rlistings": False,
            "public": False,
        }

    def test_empty(self):
        '''When no ACL is set, the returned dictionary should have empty
        lists and false rlistings and public.'''

        acl = ""
        split = split_acl(acl)

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_user_single(self):
        '''Test when one user is on the acl.'''

        acl = "tenant:user"
        split = split_acl(acl)

        self.assertEqual("tenant:user", split["users"][0])

        self.assertEqual(1, len(split["users"]))
        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_user_multiple(self):
        '''Test multiple users on the acl'''

        acl = "tenant:user1,tenant:user2,tenant:user3,user4"
        split = split_acl(acl)
        self.assertEqual(4, len(split))
        self.assertEqual("tenant:user1", split["users"][0])
        self.assertEqual("tenant:user2", split["users"][1])
        self.assertEqual("tenant:user3", split["users"][2])
        self.assertEqual("user4", split["users"][3])

        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_referrers_single(self):
        '''Test single referer on the acl'''

        acl = ".r:example.com"
        split = split_acl(acl)

        self.assertEqual(1, len(split["referrers"]))
        self.assertEqual("example.com", split["referrers"][0])

        self.assertEqual(0, len(split["users"]))
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_referrers_multiple(self):
        '''Test multiple referrers on acl'''

        acl = ".r:example.com,.r:domain.com,.r:swiftbrowser.com,.r:abc.com"
        split = split_acl(acl)

        self.assertEqual(4, len(split["referrers"]))
        self.assertEqual("example.com", split["referrers"][0])
        self.assertEqual("domain.com", split["referrers"][1])
        self.assertEqual("swiftbrowser.com", split["referrers"][2])
        self.assertEqual("abc.com", split["referrers"][3])

        self.assertEqual(0, len(split["users"]))
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_rlisting(self):
        '''Test case where rlisting is set.'''

        acl = ".rlistings"
        split = split_acl(acl)

        self.assertTrue(split["rlistings"])

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["public"])

    def test_public(self):
        '''Test when the container is set to public.'''

        acl = ".r:*"
        split = split_acl(acl)

        self.assertTrue(split["public"])

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["rlistings"])

    def test_public_rlistings(self):
        '''Test when a container is set to public and has rlistings is set.'''

        acl = ".r:*,.rlistings"
        split = split_acl(acl)

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(0, len(split["referrers"]))
        self.assertTrue(split["rlistings"])
        self.assertTrue(split["public"])

    def test_public_multiple_referrers(self):
        '''Test when a container is set to public and has multiple referrers.
        '''

        acl = ".r:*,.r:domain.com,.r:abc.com"
        split = split_acl(acl)

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(2, len(split["referrers"]))
        self.assertEqual("domain.com", split["referrers"][0])
        self.assertEqual("abc.com", split["referrers"][1])
        self.assertFalse(split["rlistings"])
        self.assertTrue(split["public"])

    def test_public_multiple_users(self):
        '''Test when a container is set to public and has multiple users.'''

        acl = ".r:*,tenant:user,user2,user3,tenant:user4"
        split = split_acl(acl)

        self.assertEqual(4, len(split["users"]))
        self.assertEqual("tenant:user", split["users"][0])
        self.assertEqual("user2", split["users"][1])
        self.assertEqual("user3", split["users"][2])
        self.assertEqual("tenant:user4", split["users"][3])
        self.assertEqual(0, len(split["referrers"]))
        self.assertFalse(split["rlistings"])
        self.assertTrue(split["public"])

    def test_rlistings_multiple_referrers(self):
        '''Test when a container has rlistings set and multiple referrers.'''

        acl = ".rlistings,.r:domain.com,.r:abc.com,.r:example.com"
        split = split_acl(acl)

        self.assertEqual(0, len(split["users"]))
        self.assertEqual(3, len(split["referrers"]))
        self.assertEqual("domain.com", split["referrers"][0])
        self.assertEqual("abc.com", split["referrers"][1])
        self.assertEqual("example.com", split["referrers"][2])
        self.assertTrue(split["rlistings"])
        self.assertFalse(split["public"])

    def test_rlistings_multiple_users(self):
        '''Test when a container has rlistings set and multiple users.'''

        acl = ".rlistings,user1,user2,tenant:user3"
        split = split_acl(acl)

        self.assertEqual(3, len(split["users"]))
        self.assertEqual("user1", split["users"][0])
        self.assertEqual("user2", split["users"][1])
        self.assertEqual("tenant:user3", split["users"][2])
        self.assertEqual(0, len(split["referrers"]))
        self.assertTrue(split["rlistings"])
        self.assertFalse(split["public"])

    def test_multiple_referrers_multiple_users(self):
        '''Test when a container has multiple referrers and multiple users.'''

        acl = ".r:domain.com,user1,user2,.r:abc.com,.r:swiftbrowser.com,user3"
        split = split_acl(acl)

        self.assertEqual(3, len(split["users"]))
        self.assertEqual("user1", split["users"][0])
        self.assertEqual("user2", split["users"][1])
        self.assertEqual("user3", split["users"][2])
        self.assertEqual(3, len(split["referrers"]))
        self.assertEqual("domain.com", split["referrers"][0])
        self.assertEqual("abc.com", split["referrers"][1])
        self.assertEqual("swiftbrowser.com", split["referrers"][2])
        self.assertFalse(split["rlistings"])
        self.assertFalse(split["public"])

    def test_public_rlistings_referrers_users(self):
        '''Test when a container has public set, rlistings set, multiple
        referrers and multiple users.'''

        acl = (".r:*,user1,.r:domain.com,user2,.rlistings,"
               "user3,.r:domain2.com,.r:abc.com")
        split = split_acl(acl)

        self.assertEqual(3, len(split["users"]))
        self.assertEqual("user1", split["users"][0])
        self.assertEqual("user2", split["users"][1])
        self.assertEqual("user3", split["users"][2])
        self.assertEqual(3, len(split["referrers"]))
        self.assertEqual("domain.com", split["referrers"][0])
        self.assertEqual("domain2.com", split["referrers"][1])
        self.assertEqual("abc.com", split["referrers"][2])
        self.assertTrue(split["rlistings"])
        self.assertTrue(split["public"])


class GetNonConsecutiveTest(TestCase):

    def test_empty(self):
        '''Test an empty set.'''

        objects = []
        self.assertEqual(get_first_nonconsecutive(objects), 1)

    def test_segment_one_missing(self):
        '''Test when segment number one is missing.'''

        objects = ["0002", "0003", "0004", "0005", "0006", "0007", "0008",
                   "0009", "0010", "0011", "0012", "0013", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 1)

    def test_sequential_numbers(self):
        '''Test a list of objects that are perfectly sequential.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0006", "0007",
                   "0008", "0009", "0010", "0011", "0012", "0013", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 15)

    def test_sequential_numbers_small(self):
        '''Test a small list of objects that are perfectly sequential.'''

        objects = ["0001", "0002"]
        self.assertEqual(get_first_nonconsecutive(objects), 3)

    def test_set_size_one(self):
        '''Test a list with one digit.'''

        objects = ["0001"]
        self.assertEqual(get_first_nonconsecutive(objects), 2)

    def test_set_size_one_incorrect(self):
        '''Test a list with one digit that is not one.'''

        objects = ["0002"]
        self.assertEqual(get_first_nonconsecutive(objects), 1)

    def test_break_in_sequence_after_one(self):
        '''Test a set where the break in sequence is after 1.'''

        objects = ["0001", "0003", "0004", "0005", "0006", "0007", "0008",
                   "0009", "0010", "0011", "0012", "0013", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 2)

    def test_break_in_sequence_middle(self):
        '''Test a break in sequence in the middle.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0007", "0008",
                   "0009", "0010", "0011", "0012", "0013", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 6)

    def test_large_break_in_sequence_middle(self):
        '''Test a break in sequence in the middle.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0014", "0015",
                   "0016"]
        self.assertEqual(get_first_nonconsecutive(objects), 6)

    def test_break_in_sequence_near_end(self):
        '''Test a break in sequence at the end.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0006", "0007",
                   "0008", "0009", "0010", "0011", "0012", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 13)

    def test_duplicate(self):
        '''Test when there is a duplicate.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0006", "0006",
                   "0007", "0008", "0009", "0010", "0011", "0012", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 7)

    def test_duplicate_break(self):
        '''Test when there is a duplicate and a break following immediately.'''

        objects = ["0001", "0002", "0003", "0004", "0005", "0006", "0006",
                   "0008", "0009", "0010", "0011", "0012", "0014"]
        self.assertEqual(get_first_nonconsecutive(objects), 7)
