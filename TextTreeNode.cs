using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TextTreeGenerator
{
  public class TextTreeNode
  {
    public string Text { private set; get; }
    public TextTreeNode Parent { private set; get; }
    public List<TextTreeNode> Children { private set; get; }
    public int StartRow { private set; get; }
    public int StartColumn { private set; get; }
    public int Depth { private set; get; }
    public int Width
    {
      get
      {
        if (null == Children || 0 == Children.Count)
        {
          return 1;
        }
        else
        {
          int iSum = Children.Sum<TextTreeNode>(
            (TextTreeNode ttnNode) =>
            {
              return ttnNode.Width;
            });
          return 2 == iSum ? 3 : iSum;
        }
      }
    }

    public bool IsOneLine
    {
      get
      {
        return 0 == Children.Count || 1 == Children.Count && Children[0].IsOneLine;
      }
    }

    public int MinChildStartRow
    {
      get
      {
        if (0 == Children.Count) return StartRow;
        else return Children[0].MinChildStartRow;
      }
    }
    public int MaxChildStartRow
    {
      get
      {
        if (0 == Children.Count) return StartRow;
        else return Children[Children.Count - 1].MaxChildStartRow;
      }
    }

    public TextTreeNode(string p_strText)
    {
      Children = new List<TextTreeNode>();
      Depth = 0;
      Text = Convert(p_strText);
    }

    public TextTreeNode(string p_strText, TextTreeNode p_ttnParent)
    {
      Children = new List<TextTreeNode>();
      Text = Convert(p_strText);
      Parent = p_ttnParent;
      p_ttnParent.AddChild(this);
      Depth = p_ttnParent.Depth + 1;
    }

    private string Convert(string p_strText)
    {
      StringBuilder sb = new StringBuilder();

      foreach (char ch in p_strText)
      {
        char chConv = ch;
        switch (ch)
        {
          case '0': chConv = '０'; break;
          case '1': chConv = '１'; break;
          case '2': chConv = '２'; break;
          case '3': chConv = '３'; break;
          case '4': chConv = '４'; break;
          case '5': chConv = '５'; break;
          case '6': chConv = '６'; break;
          case '7': chConv = '７'; break;
          case '8': chConv = '８'; break;
          case '9': chConv = '９'; break;
          case 'A': chConv = 'Ａ'; break;
          case 'B': chConv = 'Ｂ'; break;
          case 'C': chConv = 'Ｃ'; break;
          case 'D': chConv = 'Ｄ'; break;
          case 'E': chConv = 'Ｅ'; break;
          case 'F': chConv = 'Ｆ'; break;
          case 'G': chConv = 'Ｇ'; break;
          case 'H': chConv = 'Ｈ'; break;
          case 'I': chConv = 'Ｉ'; break;
          case 'J': chConv = 'Ｊ'; break;
          case 'K': chConv = 'Ｋ'; break;
          case 'L': chConv = 'Ｌ'; break;
          case 'M': chConv = 'Ｍ'; break;
          case 'N': chConv = 'Ｎ'; break;
          case 'O': chConv = 'Ｏ'; break;
          case 'P': chConv = 'Ｐ'; break;
          case 'Q': chConv = 'Ｑ'; break;
          case 'R': chConv = 'Ｒ'; break;
          case 'S': chConv = 'Ｓ'; break;
          case 'T': chConv = 'Ｔ'; break;
          case 'U': chConv = 'Ｕ'; break;
          case 'V': chConv = 'Ｖ'; break;
          case 'W': chConv = 'Ｗ'; break;
          case 'X': chConv = 'Ｘ'; break;
          case 'Y': chConv = 'Ｙ'; break;
          case 'Z': chConv = 'Ｚ'; break;
          case 'a': chConv = 'ａ'; break;
          case 'b': chConv = 'ｂ'; break;
          case 'c': chConv = 'ｃ'; break;
          case 'd': chConv = 'ｄ'; break;
          case 'e': chConv = 'ｅ'; break;
          case 'f': chConv = 'ｆ'; break;
          case 'g': chConv = 'ｇ'; break;
          case 'h': chConv = 'ｈ'; break;
          case 'i': chConv = 'ｉ'; break;
          case 'j': chConv = 'ｊ'; break;
          case 'k': chConv = 'ｋ'; break;
          case 'l': chConv = 'ｌ'; break;
          case 'm': chConv = 'ｍ'; break;
          case 'n': chConv = 'ｎ'; break;
          case 'o': chConv = 'ｏ'; break;
          case 'p': chConv = 'ｐ'; break;
          case 'q': chConv = 'ｑ'; break;
          case 'r': chConv = 'ｒ'; break;
          case 's': chConv = 'ｓ'; break;
          case 't': chConv = 'ｔ'; break;
          case 'u': chConv = 'ｕ'; break;
          case 'v': chConv = 'ｖ'; break;
          case 'w': chConv = 'ｗ'; break;
          case 'x': chConv = 'ｘ'; break;
          case 'y': chConv = 'ｙ'; break;
          case 'z': chConv = 'ｚ'; break;
          case '`': chConv = '｀'; break;
          case '~': chConv = '～'; break;
          case '!': chConv = '！'; break;
          case '@': chConv = '＠'; break;
          case '#': chConv = '＃'; break;
          case '$': chConv = '＄'; break;
          case '%': chConv = '％'; break;
          case '^': chConv = '＾'; break;
          case '&': chConv = '＆'; break;
          case '*': chConv = '＊'; break;
          case '(': chConv = '（'; break;
          case ')': chConv = '）'; break;
          case '-': chConv = '－'; break;
          case '_': chConv = '＿'; break;
          case '+': chConv = '＋'; break;
          case '=': chConv = '＝'; break;
          case '[': chConv = '［'; break;
          case '{': chConv = '｛'; break;
          case ']': chConv = '］'; break;
          case '}': chConv = '｝'; break;
          case '|': chConv = '｜'; break;
          case '\\': chConv = '＼'; break;
          case ';': chConv = '；'; break;
          case ':': chConv = '：'; break;
          case '\'': chConv = '＇'; break;
          case '"': chConv = '＂'; break;
          case ',': chConv = '，'; break;
          case '<': chConv = '＜'; break;
          case '.': chConv = '．'; break;
          case '>': chConv = '＞'; break;
          case '/': chConv = '／'; break;
          case '?': chConv = '？'; break;
        }
        sb.Append(chConv);
      }
      return sb.ToString();
    }

    public void AddChild(TextTreeNode p_ttnNode)
    {
      Children.Add(p_ttnNode);
    }

    protected void ComputeStartRow(ref int p_iRow)
    {
      if (IsOneLine)
      {
        if (Parent == null) 
            throw new Exception(string.Format("解析到[{0}]时失败", this.Text));
        if (Parent.Children.Count == 2 && this == Parent.Children[1])
        {
          StartRow = ++p_iRow;
          p_iRow++;
        }
        else
        {
          StartRow = p_iRow++;
        }

        if (Children.Count > 0)
        {
          for (TextTreeNode ttnNode = Children[0];
               ttnNode != null;
               ttnNode = ttnNode.Children.Count > 0 ? ttnNode.Children[0] : null)
          {
            ttnNode.StartRow = StartRow;
          }
        }
      }
      else
      {
        foreach (TextTreeNode ttnNode in Children)
        {
          ttnNode.ComputeStartRow(ref p_iRow);
        }
        StartRow = (Children[0].StartRow + Children[Children.Count - 1].StartRow) / 2;
      }
    }

    protected void ComputeStartColumn()
    {
      if (null == Parent)
      {
        StartColumn = 0;
      }
      else
      {
        StartColumn = Parent.StartColumn + Parent.Text.Length + 1;
      }

      foreach (TextTreeNode ttnChild in Children)
      {
        ttnChild.ComputeStartColumn();
      }
    }

    public void Compute()
    {
      int iRow = 0;
      ComputeStartRow(ref iRow);
      ComputeStartColumn();
    }


    public string Print()
    {
      List<List<string>> llStr = new List<List<string>>(MaxChildStartRow + 1);

      for (int i = 0, iLast = MaxChildStartRow; i <= iLast; i++) llStr.Add(new List<string>());

      Queue<TextTreeNode> skttnNode = new Queue<TextTreeNode>();
      skttnNode.Enqueue(this);

      while (skttnNode.Count > 0)
      {
        TextTreeNode ttnNode = skttnNode.Dequeue();
        for (int i = ttnNode.MinChildStartRow, iLast = ttnNode.MaxChildStartRow; i <= iLast; i++)
        {
          if (0 == ttnNode.Children.Count) llStr[i].Add(ttnNode.Text);
          else if (i < ttnNode.Children[0].StartRow) llStr[i].Add(new string('　', ttnNode.Text.Length + 1));
          else if (i <= ttnNode.Children[ttnNode.Children.Count - 1].StartRow)
          {
            string str = "";
            for (int j = 0; j < ttnNode.Children.Count; j++)
            {
              if (i == ttnNode.Children[j].StartRow)
              {
                if (0 == j && ttnNode.StartRow == ttnNode.Children[j].StartRow && 1 == ttnNode.Children.Count) str = ttnNode.Text + "─";
                else if (0 == j) str = new string('　', ttnNode.Text.Length) + "┌";
                else if (ttnNode.Children.Count - 1 == j) str = new string('　', ttnNode.Text.Length) + "└";
                else if (ttnNode.StartRow == ttnNode.Children[j].StartRow) str = ttnNode.Text + "┼";
                else str = new string('　', ttnNode.Text.Length) + "├";
                break;
              }
            }

            if ("" == str)
            {
              str = (ttnNode.StartRow == i ? ttnNode.Text + "┤" : new string('　', ttnNode.Text.Length) + "│");
            }

            llStr[i].Add(str);
          }
          else llStr[i].Add(new string('　', ttnNode.Text.Length + 1));
        }
        foreach (TextTreeNode ttnChild in ttnNode.Children) skttnNode.Enqueue(ttnChild);
      }

      StringBuilder sb = new StringBuilder();

      foreach (List<string> lstr in llStr)
      {
        foreach (string str in lstr) sb.Append(str);
        sb.AppendLine();
      }
      return sb.ToString().TrimEnd('\r','\n');
    }

    public static List<TextTreeNode> Parse(string[] p_astrLines)
    {
      List<TextTreeNode> lttnRoot = new List<TextTreeNode>();
      Stack<TextTreeNode> skttnNode = new Stack<TextTreeNode>();
      int i = 0;
      for (; i < p_astrLines.Length; i++)
      {
          string line = p_astrLines[i];
          if ("" == line.Trim()) continue;

          int j = 0;
          for (; j < line.Length && "#-_$@*%".Contains(line[j]); j++) ;
          if (j >= line.Length) return null;

          if (0 == j)
          {
              TextTreeNode ttnRoot = new TextTreeNode(line);
              lttnRoot.Add(ttnRoot);
              skttnNode.Clear();
              skttnNode.Push(ttnRoot);
          }
          else
          {
              while (j < skttnNode.Peek().Depth) skttnNode.Pop();
              TextTreeNode ttnNodeLast = skttnNode.Peek();

              //是上个节点的孩子
              if (j == ttnNodeLast.Depth + 1)
              {
                  skttnNode.Push(new TextTreeNode(line.Substring(j), ttnNodeLast));
              }
              //是上个节点的平级
              else if (j == ttnNodeLast.Depth)
              {
                  skttnNode.Push(new TextTreeNode(line.Substring(j), ttnNodeLast.Parent));
              }
              else
              {
                  throw new Exception(string.Format("解析第{0}行[{1}]时失败", i + 1, p_astrLines[i]));
                  return null;
              }
          }
      }
      foreach (TextTreeNode ttnRoot in lttnRoot)
      {
        ttnRoot.Compute();
      }
      return lttnRoot;
    }
  }
}
