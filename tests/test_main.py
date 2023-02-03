from unittest import TestCase

import sublime


class TestMain(TestCase):
    CONTENT = '''
# first line
class MyClass:
    def method1(self):
        """
        multi-line comment

        multi-line comment
        """
        self.do_something()
        # single-line comment
        self.do_something()

    # def method2(self):
    #     self.do_something()

    #     self.do_something()
    '''

    def setUp(self):
        self.window = sublime.active_window()

        self.view = self.window.new_file(0)
        self.view.run_command("insert", {"characters": self.CONTENT.strip()})
        self.view.set_syntax_file('Packages/Python/Python.sublime-syntax')

        settings = sublime.load_settings('Preferences.sublime-settings')
        settings.set('close_windows_when_empty', False)
        settings.set('auto_indent', False)

    def tearDown(self):
        if self.view and self.window:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.window.run_command('close_file')

    def runOnLine(self, line, eol=False):
        if self.view and self.window:
            self.window.focus_view(self.view)
            self.view.run_command('goto_line', {'line': line})
            if eol:
                self.view.run_command('move_to', {'to': 'eol'})
            # run the sync command
            self.view.run_command('expand_selection_to_comments_atomic')

    def assertSelection(self, expected):
        self.assertEqual(self.view.substr(self.view.sel()[0]), expected)

    def test_multi_line(self):
        self.runOnLine(6)

        self.assertSelection(
            '''
        """
        multi-line comment

        multi-line comment
        """
            '''.strip()
        )

    def test_single_line_beginning_of_line(self):
        self.runOnLine(10)

        self.assertSelection("        # single-line comment")

    def test_single_line_end_of_line(self):
        self.runOnLine(10, eol=True)

        self.assertSelection("# single-line comment")

    def test_multiple_single_line(self):
        self.runOnLine(14, eol=True)

        self.assertSelection(
            '''
    # def method2(self):
    #     self.do_something()

    #     self.do_something()
            '''.strip()
        )

    def test_first_line(self):
        self.runOnLine(1)

        self.assertSelection("# first line")

    def test_last_line_end_of_line(self):
        self.runOnLine(16, eol=True)

        self.assertSelection(
            '''
    # def method2(self):
    #     self.do_something()

    #     self.do_something()
            '''.strip()
        )
