import libadalang as lal
from src.types import Buffer
from src.interfaces import ChunkInterface, StrategyInterface
from src.dichotomy import dichotomize


class RemoveClause(ChunkInterface):
    def __init__(self, buffer, node):
        self.buffer = buffer
        self.node = node

    def do(self):
        num_lines = self.node.sloc_range.end.line - self.node.sloc_range.start.line + 1
        new_text = [""] * num_lines
        self.range, self.lines = self.buffer.replace(self.node.sloc_range, new_text)

    def undo(self):
        self.buffer.replace(self.range, self.lines)


class RemoveImports(StrategyInterface):
    """ Remove subprograms """

    def save(self):
        for file in self.buffers:
            self.buffers[file].save()

    def run_on_file(self, context, file, predicate):
        self.buffers = {file: Buffer(file)}
        unit = context.get_from_file(file)

        if unit.root is None:
            return

        chunks = []

        # First remove all the use clauses that we can, then
        # try with clauses

        for type in (lal.UsePackageClause, lal.WithClause):

            for node in unit.root.findall(lambda x: x.is_a(type)):
                # Create a chunk for each clause
                chunks.append(RemoveClause(self.buffers[file], node))

            dichotomize(chunks, predicate, self.save)
