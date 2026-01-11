import InputNode from './InputNode';
import KnowledgeBaseNode from './KnowledgeBaseNode';
import LLMNode from './LLMNode';
import OutputNode from './OutputNode';

export const nodeTypes = {
  input: InputNode,
  knowledgebase: KnowledgeBaseNode,
  llm: LLMNode,
  output: OutputNode,
};

export { InputNode, KnowledgeBaseNode, LLMNode, OutputNode };
