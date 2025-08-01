using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace TextTreeGenerator
{
  public partial class MainForm : Form
  {
    public MainForm()
    {
      InitializeComponent();
    }

    private void m_btnGenerate_Click(object sender, EventArgs e)
    {
        try
        {
            string[] astrLines = m_tbxInput.Text.Split(new string[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries);

            var lttnNode = TextTreeNode.Parse(astrLines);

            StringBuilder sb = new StringBuilder();

            foreach (var ttnNode in lttnNode)
            {
                sb.AppendLine(ttnNode.Print());
            }

            m_tbxOutput.Text = sb.ToString();
        }
        catch (Exception ex)
        {
            MessageBox.Show("生成失败，原因：" + ex.Message);
        }

    }
  }
}
