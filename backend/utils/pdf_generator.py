"""
PDF Report Generator for Origo Analysis Results
Generates comprehensive PDF reports with overview, paragraph, sentence, and word analysis
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """
    Generates comprehensive PDF reports for Origo analysis results
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.Color(0.1, 0.125, 0.17)  # #1a202c
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.Color(0.1, 0.125, 0.17)
        ))
        
        # Subsection heading style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.Color(0.1, 0.125, 0.17)
        ))
        
        # Score text style
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceBefore=5,
            spaceAfter=5
        ))
        
        # Content text style
        self.styles.add(ParagraphStyle(
            name='ContentText',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=3,
            spaceAfter=3
        ))
    
    def _get_score_color(self, score: float) -> colors.Color:
        """Get color based on score value"""
        if score >= 0.7:
            return colors.Color(0.87, 0.27, 0.15)  # Red #dc2626
        elif score >= 0.6:  # Changed from 0.4 to 0.6
            return colors.Color(0.96, 0.62, 0.07)  # Yellow #f59e0b
        else:
            return colors.Color(0.06, 0.73, 0.51)  # Green #10b981
    
    def _format_score(self, score: float) -> str:
        """Format score as percentage"""
        return f"{int(score * 100)}%"
    
    def generate_report(self, report_data: Dict[str, Any]) -> BytesIO:
        """
        Generate a comprehensive PDF report
        Args:
            report_data: Dictionary containing analysis results
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page(report_data))
        story.append(PageBreak())
        
        # Overview section
        story.extend(self._create_overview_section(report_data['overview']))
        story.append(PageBreak())
        
        # Paragraph analysis section
        if report_data['paragraphs']:
            story.extend(self._create_paragraph_section(report_data['paragraphs']))
            story.append(PageBreak())
        
        # Sentence analysis section
        if report_data['sentences']:
            story.extend(self._create_sentence_section(report_data['sentences']))
            story.append(PageBreak())
        
        # Word analysis section
        if report_data['words']:
            story.extend(self._create_word_section(report_data['words']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_title_page(self, report_data: Dict[str, Any]) -> List:
        """Create the title page"""
        story = []
        
        # Main title
        story.append(Paragraph("Origo AI Detection Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Text Analysis Results", self.styles['Heading2']))
        story.append(Spacer(1, 30))
        
        # Overall score display
        overall_score = report_data['overview']['overall_score']
        score_color = self._get_score_color(overall_score)
        
        story.append(Paragraph("Overall AI Probability", self.styles['SectionHeading']))
        story.append(Paragraph(
            f"<font color='{score_color}'><b>{self._format_score(overall_score)}</b></font>",
            self.styles['ScoreText']
        ))
        story.append(Spacer(1, 30))
        
        # Generation info
        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {generation_time}", self.styles['Normal']))
        
        # Metadata
        metadata = report_data['overview'].get('metadata', {})
        if metadata:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Text Statistics", self.styles['SectionHeading']))
            
            metadata_data = [
                ['Characters', f"{metadata.get('text_length', 'N/A'):,}"],
                ['Words', f"{metadata.get('word_count', 'N/A'):,}"],
                ['Sentences', f"{metadata.get('sentence_count', 'N/A'):,}"],
                ['Paragraphs', f"{metadata.get('paragraph_count', 'N/A'):,}"]
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 2*inch])
            metadata_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            story.append(metadata_table)
        
        return story
    
    def _create_overview_section(self, overview_data: Dict[str, Any]) -> List:
        """Create the overview section with global scores"""
        story = []
        
        story.append(Paragraph("Analysis Overview", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Global scores
        story.append(Paragraph("Component Scores", self.styles['SectionHeading']))
        story.append(Spacer(1, 10))
        
        global_scores = overview_data.get('global_scores', {})
        weights = overview_data.get('metadata', {}).get('weights_used', {})
        
        score_data = [['Component', 'Score', 'Weight', 'Description']]
        
        component_descriptions = {
            'perplexity': 'GPT-2 language model perplexity analysis',
            'burstiness': 'Sentence structure and length variation',
            'semantic_coherence': 'Semantic flow and consistency patterns',
            'ngram_similarity': 'N-gram repetition and similarity patterns'
        }
        
        for component, score in global_scores.items():
            weight = weights.get(component, 0.25)
            description = component_descriptions.get(component, 'Analysis component')
            score_color = self._get_score_color(score)
            
            score_data.append([
                component.replace('_', ' ').title(),
                f"<font color='{score_color}'><b>{self._format_score(score)}</b></font>",
                f"{int(weight * 100)}%",
                description
            ])
        
        score_table = Table(score_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3*inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(score_table)
        
        # Score interpretation
        story.append(Spacer(1, 20))
        story.append(Paragraph("Score Interpretation", self.styles['SectionHeading']))
        
        interpretation_text = """
        <b>Score Ranges:</b><br/>
        • 0-40%: Low AI probability (likely human-written)<br/>
        • 40-70%: Medium AI probability (uncertain)<br/>
        • 70-100%: High AI probability (likely AI-generated)<br/><br/>
        
        <b>Analysis Components:</b><br/>
        • <b>Perplexity</b>: Measures text predictability using GPT-2. Higher scores indicate more predictable patterns typical of AI.<br/>
        • <b>Burstiness</b>: Analyzes variation in sentence structure. Lower variation suggests AI generation.<br/>
        • <b>Semantic Coherence</b>: Examines semantic flow consistency. Extreme values may indicate AI.<br/>
        • <b>N-gram Similarity</b>: Detects repetitive patterns common in AI-generated text.
        """
        
        story.append(Paragraph(interpretation_text, self.styles['Normal']))
        
        return story
    
    def _create_paragraph_section(self, paragraphs: List[Dict[str, Any]]) -> List:
        """Create the paragraph analysis section"""
        story = []
        
        story.append(Paragraph("Paragraph Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Showing {len(paragraphs)} paragraphs with significant AI probability (≥40%)", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        for i, paragraph in enumerate(paragraphs, 1):
            score = paragraph['score']
            score_color = self._get_score_color(score)
            
            # Paragraph header
            story.append(Paragraph(f"Paragraph {i}", self.styles['SubsectionHeading']))
            story.append(Paragraph(
                f"<font color='{score_color}'><b>AI Probability: {self._format_score(score)}</b></font>",
                self.styles['ScoreText']
            ))
            story.append(Spacer(1, 8))
            
            # Paragraph text
            story.append(Paragraph(paragraph['text'], self.styles['ContentText']))
            story.append(Spacer(1, 15))
            
            if i < len(paragraphs):
                story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
                story.append(Spacer(1, 10))
        
        return story
    
    def _create_sentence_section(self, sentences: List[Dict[str, Any]]) -> List:
        """Create the sentence analysis section"""
        story = []
        
        story.append(Paragraph("Sentence Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Showing {len(sentences)} sentences with significant AI probability (≥40%)", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        for i, sentence in enumerate(sentences, 1):
            score = sentence['score']
            score_color = self._get_score_color(score)
            
            # Sentence header
            story.append(Paragraph(f"Sentence {i}", self.styles['SubsectionHeading']))
            story.append(Paragraph(
                f"<font color='{score_color}'><b>AI Probability: {self._format_score(score)}</b></font>",
                self.styles['ScoreText']
            ))
            story.append(Spacer(1, 8))
            
            # Sentence text
            story.append(Paragraph(sentence['text'], self.styles['ContentText']))
            story.append(Spacer(1, 15))
            
            if i < len(sentences):
                story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
                story.append(Spacer(1, 10))
        
        return story
    
    def _create_word_section(self, words: List[Dict[str, Any]]) -> List:
        """Create the word analysis section"""
        story = []
        
        story.append(Paragraph("Word Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Showing {len(words)} words with significant AI probability (≥40%)", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Create table data
        word_data = [['Rank', 'Word', 'AI Probability', 'Frequency', 'Impact']]
        
        for i, word in enumerate(words, 1):
            score = word['average_score']
            count = word['count']
            impact = score * count
            score_color = self._get_score_color(score)
            
            word_data.append([
                str(i),
                word['word'],
                f"<font color='{score_color}'><b>{self._format_score(score)}</b></font>",
                str(count),
                f"{impact:.2f}"
            ])
        
        # Create table
        word_table = Table(word_data, colWidths=[0.8*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
        word_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(word_table)
        
        # Word analysis explanation
        story.append(Spacer(1, 20))
        story.append(Paragraph("Word Analysis Explanation", self.styles['SectionHeading']))
        
        explanation_text = """
        The word analysis shows individual words that contribute to the overall AI detection score.
        Words are ranked by their AI probability score, with higher scores indicating patterns more
        typical of AI-generated text. The frequency shows how often each word appears in the text,
        and the impact represents the word's overall contribution to the final score.
        """
        
        story.append(Paragraph(explanation_text, self.styles['Normal']))
        
        return story

# Global PDF generator instance
pdf_generator = PDFReportGenerator()