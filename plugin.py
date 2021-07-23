import re

import sublime
import sublime_plugin


class ExpandSelectionToCommentsCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction=None):
        # enable soft-undo
        sublime.set_timeout(lambda:
            self.view.run_command('expand_selection_to_comments_atomic', { 'direction': direction }),
            0
        )

class ExpandSelectionToCommentsAtomicCommand(sublime_plugin.TextCommand):
    DIRECTION_UP = 'up'
    DIRECTION_DOWN = 'down'

    def __init__(self, view):
        super().__init__(view)

        self.view_range = range(0, self.view.size() + 1)

    def run(self, edit, direction=None):
        for region in self.view.sel():
            begin = region_begin = region.begin()
            end = region_end = region.end()

            if direction == self.DIRECTION_UP or direction != self.DIRECTION_DOWN:
                region_begin = self.find_region_boundary(begin, False)

            if direction == self.DIRECTION_DOWN or direction != self.DIRECTION_UP:
                region_end = self.find_region_boundary(end, True)

            if begin != region_begin or end != region_end:
                self.view.sel().add(sublime.Region(region_begin, region_end))

    def find_region_boundary(self, start, forward=True):
        res = cur = start

        while self.is_withint_comment(cur):
            if self.is_comment(cur) or self.is_last_comment_char(cur):
                res = cur

            if forward:
                cur += 1
            else:
                cur -= 1

        return res

    def is_comment(self, point):
        return self.view.match_selector(point, 'comment')

    def is_last_comment_char(self, point):
        """
        Check whether the point is on the last char in the line and there is a comment char before
        Mostly to cover this case:

        # comment goes here
                          ^ -> cursor is here and there is no trailing newline

        Without this check this character is simple ignored
        """
        return (self.view.classify(point) & sublime.CLASS_LINE_END != 0) and self.is_comment(point - 1)

    def is_withint_comment(self, point):
        if point not in self.view_range:
            return False

        char = self.view.substr(point)

        return self.is_comment(point) or re.match(r'\s', char) or self.is_last_comment_char(point)
