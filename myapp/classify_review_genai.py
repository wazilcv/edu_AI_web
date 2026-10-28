import google.generativeai as genai
import json
from typing import List, Dict, Tuple


class GeminiFeedbackAnalyzer:
    def __init__(self, api_key: str):
        """Initialize Gemini AI analyzer"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_single_feedback(self, text: str, feedback_id: int = 1) -> Dict:
        """Analyze a single feedback item with detailed categorization"""
        prompt = f"""
        Analyze this educational feedback thoroughly:

        TEXT: "{text}"

        Provide detailed analysis in this JSON format:
        {{
            "feedback_id": {feedback_id},
            "overall_sentiment": "Positive/Negative/Neutral",
            "sentiment_score": 1-10,
            "teaching_clarity_score": 1-5,
            "content_quality_score": 1-5,
            "practical_value_score": 1-5,
            "primary_emotion": "frustration/satisfaction/confusion/etc",
            "strengths_mentioned": ["strength1", "strength2"],
            "weaknesses_mentioned": ["weakness1", "weakness2"],
            "suggestions_provided": ["suggestion1", "suggestion2"],
            "urgency_level": "High/Medium/Low",
            "action_items": ["item1", "item2"],
            "one_sentence_summary": "summary here"
        }}

        Be objective and specific. Return ONLY valid JSON.
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = self._clean_response(response.text)
            result = json.loads(response_text)
            result["original_text_preview"] = text[:100] + "..." if len(text) > 100 else text
            return result
        except Exception as e:
            print(f"Error analyzing feedback {feedback_id}: {e}")
            return self._create_error_result(feedback_id, text)

    def _clean_response(self, response_text: str) -> str:
        """Clean the response text and extract JSON"""
        # Remove markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return response_text.strip()

    def _create_error_result(self, feedback_id: int, text: str) -> Dict:
        """Create error result when analysis fails"""
        return {
            "feedback_id": feedback_id,
            "overall_sentiment": "Error",
            "sentiment_score": 0,
            "teaching_clarity_score": 0,
            "content_quality_score": 0,
            "practical_value_score": 0,
            "primary_emotion": "unknown",
            "strengths_mentioned": [],
            "weaknesses_mentioned": [],
            "suggestions_provided": [],
            "urgency_level": "Unknown",
            "action_items": [],
            "one_sentence_summary": "Analysis failed",
            "original_text_preview": text[:100] + "..." if len(text) > 100 else text
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple feedback items"""
        results = []
        print("Analyzing feedback...")

        for idx, text in enumerate(texts, 1):
            print(f"  Processing item {idx}/{len(texts)}")
            result = self.analyze_single_feedback(text, idx)
            results.append(result)

        return results

    def generate_comprehensive_report(self, analysis_results: List[Dict]) -> Dict:
        """Generate comprehensive report from all analyses"""
        report = {
            "total_feedbacks": len(analysis_results),
            "sentiment_distribution": {},
            "average_scores": {},
            "top_strengths": [],
            "top_weaknesses": [],
            "common_suggestions": [],
            "priority_areas": []
        }

        # Calculate sentiment distribution
        sentiments = [r.get("overall_sentiment", "Unknown") for r in analysis_results]
        from collections import Counter
        report["sentiment_distribution"] = dict(Counter(sentiments))

        # Calculate average scores
        scores = ["sentiment_score", "teaching_clarity_score",
                  "content_quality_score", "practical_value_score"]

        for score in scores:
            valid_scores = [r.get(score, 0) for r in analysis_results if isinstance(r.get(score), (int, float))]
            if valid_scores:
                report["average_scores"][score] = sum(valid_scores) / len(valid_scores)

        # Collect all strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        all_suggestions = []

        for result in analysis_results:
            all_strengths.extend(result.get("strengths_mentioned", []))
            all_weaknesses.extend(result.get("weaknesses_mentioned", []))
            all_suggestions.extend(result.get("suggestions_provided", []))

        # Find most common items
        def get_most_common(items, n=3):
            from collections import Counter
            return [item for item, _ in Counter(items).most_common(n)]

        report["top_strengths"] = get_most_common(all_strengths)
        report["top_weaknesses"] = get_most_common(all_weaknesses)
        report["common_suggestions"] = get_most_common(all_suggestions)

        # Determine priority areas based on urgency and frequency
        high_urgency = [r for r in analysis_results if r.get("urgency_level") == "High"]
        if high_urgency:
            urgent_weaknesses = []
            for r in high_urgency:
                urgent_weaknesses.extend(r.get("weaknesses_mentioned", []))
            report["priority_areas"] = get_most_common(urgent_weaknesses)

        return report


# Usage Example
def run_analysis(feedback_list):
    # Your API key (get from https://makersuite.google.com/app/apikey)
    API_KEY = "AIzaSyCIHagpTMb60QHutBYRJMND5jlzc-IowEs"



    # Initialize analyzer
    analyzer = GeminiFeedbackAnalyzer(API_KEY)

    # Analyze all feedback
    print("🎯 Starting Gemini AI Analysis...")
    results = analyzer.analyze_batch(feedback_list)

    # Display individual results
    print("\n📋 INDIVIDUAL FEEDBACK ANALYSIS:")
    print("=" * 80)
    for result in results:
        print(f"\nFeedback #{result['feedback_id']}")
        print(f"Preview: {result['original_text_preview']}")
        print(f"Sentiment: {result['overall_sentiment']} (Score: {result['sentiment_score']}/10)")
        print(f"Summary: {result['one_sentence_summary']}")
        print(f"Urgency: {result['urgency_level']}")
        if result['strengths_mentioned']:
            print(f"Strengths: {', '.join(result['strengths_mentioned'][:2])}")
        if result['weaknesses_mentioned']:
            print(f"Weaknesses: {', '.join(result['weaknesses_mentioned'][:2])}")
        print("-" * 60)

    # Generate comprehensive report
    print("\n📊 COMPREHENSIVE REPORT:")
    print("=" * 80)
    report = analyzer.generate_comprehensive_report(results)

    print(f"\nTotal Feedbacks Analyzed: {report['total_feedbacks']}")

    res_txt =[]
    print(f"\nSentiment Distribution:")
    for sentiment, count in report['sentiment_distribution'].items():
        percentage = (count / report['total_feedbacks']) * 100
        print(f"  {sentiment}: {count} ({percentage:.1f}%)")

    print(f"\nAverage Scores:")
    for score_name, avg_score in report['average_scores'].items():
        print(f"  {score_name}: {avg_score:.2f}")

    if report['top_strengths']:
        print(f"\nTop Strengths:")
        res_txt.append("Top Strengths")
        for strength in report['top_strengths']:
            print(f"  • {strength}")
            res_txt.append(strength)


    if report['top_weaknesses']:
        print(f"\nTop Areas Needing Improvement:")
        res_txt.append(" ")
        res_txt.append("")
        res_txt.append("Top Weaknesses")
        for weakness in report['top_weaknesses']:
            print(f"  • {weakness}")
            res_txt.append(weakness)

    if report['common_suggestions']:
        print(f"\nCommon Suggestions:")
        res_txt.append("")
        res_txt.append("")
        res_txt.append("Common suggestions")
        for suggestion in report['common_suggestions']:
            print(f"  • {suggestion}")
            res_txt.append(suggestion)

    if report['priority_areas']:
        print(f"\n🚨 Priority Areas (High Urgency):")
        res_txt.append("")
        res_txt.append("")
        res_txt.append("Priority Areas")
        for area in report['priority_areas']:
            print(f"  ⚠️  {area}")
            res_txt.append(area)
    return res_txt

# if __name__ == "__main__":
#     run_analysis()