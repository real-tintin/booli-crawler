import queue


class PageQueue(queue.Queue, object):

    def __init__(self, pages: [int]):
        super(PageQueue, self).__init__()

        for page in pages:
            self.put(page)
