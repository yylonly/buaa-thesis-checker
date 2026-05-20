#r "nuget: DocumentFormat.OpenXml, 3.2.0"

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

string outputPath = Args[0];
string[] content = Args.Skip(1).ToArray();

using var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document();
var body = new Body();

var sectPr = new SectionProperties(
    new PageSize { Width = 11906, Height = 16838 },
    new PageMargin { Top = 1440, Right = 1440, Bottom = 1440, Left = 1440 }
);

Paragraph CreateHeading(string text, int level) {
    var p = new Paragraph();
    var r = new Run();
    var rPr = new RunProperties(new Bold());
    rPr.Append(new FontSize { Val = level == 1 ? "32" : "28" });
    r.Append(rPr);
    r.Append(new Text(text));
    p.Append(r);
    return p;
}

Paragraph CreatePara(string text) {
    var p = new Paragraph();
    var r = new Run();
    r.Append(new Text(text));
    p.Append(r);
    return p;
}

Paragraph CreateBullet(string text) {
    var p = new Paragraph();
    var r = new Run();
    r.Append(new Text("• " + text));
    p.Append(r);
    return p;
}

Paragraph CreateBoldPara(string text) {
    var p = new Paragraph();
    var r = new Run();
    var rPr = new RunProperties(new Bold());
    r.Append(rPr);
    r.Append(new Text(text));
    p.Append(r);
    return p;
}

// Process content array - format: ["type:text", ...]
foreach (var item in content) {
    if (item.StartsWith("H1:")) {
        body.Append(CreateHeading(item.Substring(3), 1));
    } else if (item.StartsWith("H2:")) {
        body.Append(CreateHeading(item.Substring(3), 2));
    } else if (item.StartsWith("BOLD:")) {
        body.Append(CreateBoldPara(item.Substring(5)));
    } else if (item.StartsWith("BULLET:")) {
        body.Append(CreateBullet(item.Substring(7)));
    } else if (item.StartsWith("SPACE:")) {
        body.Append(CreatePara(item.Substring(6)));
    } else {
        body.Append(CreatePara(item));
    }
}

body.Append(sectPr);
mainPart.Document.Append(body);

Console.WriteLine("Document created: " + outputPath);
