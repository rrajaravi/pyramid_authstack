import unittest


class MultiAuthenticationPolicyTests(unittest.TestCase):
    def MultiAuthenticationPolicy(self, *a, **kw):
        from . import MultiAuthenticationPolicy
        return MultiAuthenticationPolicy(*a, **kw)

    def test_add_policy_new_policy(self):
        policy = self.MultiAuthenticationPolicy()
        policy.add_policy('foo', 'dummy')
        self.assertEqual(len(policy.policies), 1)
        self.assertTrue('foo' in policy.policies)

    def test_add_policy_replace_policy(self):
        policy = self.MultiAuthenticationPolicy()
        policy.add_policy('foo', 'dummy')
        policy.add_policy('foo', 'other')
        self.assertEqual(len(policy.policies), 1)
        self.assertEqual(policy.policies['foo'], 'other')

    def test_unauthenticated_userid_no_policies(self):
        policy = self.MultiAuthenticationPolicy()
        self.assertEqual(policy.unauthenticated_userid(None), None)

    def test_unauthenticated_userid_call_subpolicy(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        sub_policy.unauthenticated_userid.return_value = 'userid'
        policy.add_policy('sub', sub_policy)
        self.assertEqual(policy.unauthenticated_userid('request'), 'userid')
        sub_policy.unauthenticated_userid.assert_called_once_with('request')

    def test_unauthenticated_userid_prefer_first_policy(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        for i in [1, 2]:
            sub_policy = mock.Mock()
            sub_policy.unauthenticated_userid.return_value = i
            policy.add_policy('sub%d' % i, sub_policy)
        self.assertEqual(policy.unauthenticated_userid(None), 1)

    def test_efffective_principals_no_policies(self):
        from pyramid.authentication import Everyone
        policy = self.MultiAuthenticationPolicy()
        self.assertEqual(policy.effective_principals(None), [Everyone])

    def test_efffective_principals_add_policy_delegate_to_subpolicy(self):
        from pyramid.authentication import Authenticated
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        sub_policy.effective_principals.return_value = ['principal']
        policy.add_policy('sub', sub_policy)
        self.assertTrue('principal' in policy.effective_principals('request'))
        sub_policy.effective_principals.assert_called_once_with('request')

    def test_efffective_principals_add_policy_name_as_principal_if_it_authenticates(self):
        from pyramid.authentication import Authenticated
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        sub_policy.effective_principals.return_value = []
        policy.add_policy('sub', sub_policy)
        self.assertTrue('auth:sub' not in policy.effective_principals(None))
        sub_policy.effective_principals.return_value = [Authenticated]
        self.assertTrue('auth:sub' in policy.effective_principals(None))

    def test_remember_no_policies(self):
        policy = self.MultiAuthenticationPolicy()
        policy.remember('request', 'principal')

    def test_remember_delegate_to_subpolicy(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        policy.add_policy('sub', sub_policy)
        policy.remember('request', 'principal', extra='option')
        sub_policy.remember.assert_called_once_with('request', 'principal', extra='option')

    def test_remember_policy_filter(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        policy.add_policy('sub', sub_policy)
        policy.remember('request', 'principal', policies=[])
        self.assertTrue(not sub_policy.remember.called)
        policy.remember('request', 'principal', policies=['sub'])
        sub_policy.remember.assert_called_once_with('request', 'principal')

    def test_forget_no_policies(self):
        policy = self.MultiAuthenticationPolicy()
        policy.forget('request')

    def test_forget_delegate_to_subpolicy(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        policy.add_policy('sub', sub_policy)
        policy.forget('request')
        sub_policy.forget.assert_called_once_with('request')

    def test_forget_policy_filter(self):
        import mock
        policy = self.MultiAuthenticationPolicy()
        sub_policy = mock.Mock()
        policy.add_policy('sub', sub_policy)
        policy.forget('request', policies=[])
        self.assertTrue(not sub_policy.forget.called)
        policy.forget('request', policies=['sub'])
        sub_policy.forget.assert_called_once_with('request')

