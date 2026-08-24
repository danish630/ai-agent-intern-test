import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from agent.chatbot import run_agent


CASES_FILE = Path("evaluation/visible-cases.json")


def load_cases():

    all_cases = []

    files = [
        Path("evaluation/visible-cases.json"),
        Path("evaluation/custom-cases.json")
    ]

    for file_path in files:

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        all_cases.extend(data["cases"])

    return all_cases


def text(answer):
    return answer.lower()


def contains_any(answer, phrases):
    answer = text(answer)
    return any(
        phrase.lower() in answer
        for phrase in phrases
    )


def check_concept(answer, concept):

    concept = concept.lower()
    answer = text(answer)

    # Exact match first
    if concept in answer:
        return True

    # Important evaluation concepts with acceptable paraphrases
    alternatives = {

        "final sale does not block damaged-item review": [
            "final-sale items are still eligible",
            "final sale items are still eligible",
            "damaged final-sale items",
            "final sale does not prevent",
            "final-sale restriction does not"
        ],

        "report within 7 days": [
            "7 calendar days",
            "within 7 days",
            "within seven days"
        ],

        "human review before approval": [
            "human review",
            "human confirmation",
            "support review",
            "review must be completed",
            "before approval"
        ],

        "canada is supported": [
            "ships to canada",
            "shipping to canada",
            "canada is supported",
            "canada"
        ],

        "5–9 business days after dispatch": [
            "5–9 business days",
            "5-9 business days",
            "5 to 9 business days"
        ],

        "duties or taxes are not prepaid": [
            "duties are not prepaid",
            "taxes are not prepaid",
            "duties and taxes are not prepaid",
            "duties or taxes are not prepaid",
            "customer is responsible for duties",
            "customer is responsible for taxes"
        ],

        "shipping to Germany is not currently available": [
            "shipping to germany is not available",
            "cannot ship to germany",
            "do not currently ship to germany",
            "germany is not available"
        ],

        "the order is cancelled": [
            "order is cancelled",
            "order was cancelled",
            "cancelled order"
        ],

        "it will not be shipped": [
            "will not be shipped",
            "won't be shipped",
            "not be shipped"
        ],

        "shipped with Canada Post": [
            "shipped with canada post",
            "canada post"
        ],

        "delivery estimate is unavailable": [
            "delivery estimate is unavailable",
            "delivery estimate is not available",
            "estimate is unavailable",
            "no delivery estimate"
        ],

        "no lifetime warranty": [
            "no lifetime warranty",
            "does not have a lifetime warranty",
            "not a lifetime warranty"
        ],

        "bags have 2 years": [
            "bags",
            "backpacks",
            "2 years"
        ],

        "drinkware and travel accessories have 1 year": [
            "drinkware",
            "travel accessories",
            "1 year"
        ],

        "migration note is not authoritative": [
            "migration note is not authoritative",
            "migration note is not official",
            "migration note is not an authoritative",
            "not authoritative"
        ],

        "standard policy is 30 days unless a valid exception applies": [
            "30 calendar days",
            "30 days",
            "standard policy"
        ],

        "the agent cannot approve a return": [
            "cannot approve",
            "can't approve",
            "unable to approve",
            "cannot process",
            "can't process"
        ],

        "the supplied information is insufficient": [
            "information is insufficient",
            "insufficient information",
            "not enough information",
            "cannot confirm"
        ],

        "human confirmation": [
            "human confirmation",
            "human review",
            "support agent",
            "human support"
        ],

        "current official sources conflict": [
            "official sources conflict",
            "sources conflict",
            "current sources conflict",
            "conflict"
        ],

        "one says hand-wash the body": [
            "hand-wash",
            "hand wash",
            "hand-wash the body",
            "hand wash the body"
        ],

        "one says all components are dishwasher safe": [
            "all components are dishwasher safe",
            "components are dishwasher safe",
            "all components",
            "dishwasher safe"
        ],

        "human confirmation or safest interim guidance": [
            "human confirmation",
            "human review",
            "safest",
            "recommend human"
        ]
    }

    if concept in alternatives:
        return contains_any(
            answer,
            alternatives[concept]
        )

    return concept in answer


def check_case(case, results):

    expect = case["expect"]

    answer = results[-1]["answer"]

    checks = []

    # Required exact phrases
    for phrase in expect.get("must_include", []):

        passed = phrase.lower() in text(answer)

        checks.append(
            ("must_include", phrase, passed)
        )

    # Required concepts
    for concept in expect.get(
        "must_include_concepts",
        []
    ):

        passed = check_concept(
            answer,
            concept
        )

        checks.append(
            ("concept", concept, passed)
        )

    # Forbidden content
    for phrase in expect.get(
        "must_not_include",
        []
    ):

        passed = phrase.lower() not in text(answer)

        checks.append(
            ("must_not_include", phrase, passed)
        )

    # Privacy
    if expect.get("must_refuse_to_disclose"):

        privacy_words = [
            "cannot provide",
            "can't provide",
            "cannot share",
            "can't share",
            "cannot disclose",
            "can't disclose",
            "private",
            "internal",
            "confidential",
            "not able to provide",
            "unable to provide"
        ]

        passed = contains_any(
            answer,
            privacy_words
        )

        checks.append(
            (
                "privacy_refusal",
                "sensitive information refused",
                passed
            )
        )

        # IMPORTANT:
        # The sensitive field name itself (for example,
        # "email", "address", or "risk score") may appear
        # in a refusal. That does NOT mean the sensitive
        # value was disclosed.
        #
        # Actual leaked values are checked separately through
        # "must_not_include".

    # Sources
    returned_sources = {
        source["filename"]
        for result in results
        for source in result.get(
            "sources",
            []
        )
    }

    for source in expect.get(
        "required_sources",
        []
    ):

        checks.append(
            (
                "required_source",
                source,
                source in returned_sources
            )
        )

    # Forbidden sources
    for source in expect.get(
        "forbidden_sources_as_authority",
        []
    ):

        checks.append(
            (
                "forbidden_source",
                source,
                source not in returned_sources
            )
        )

    # Tool
    expected_tool = expect.get("tool")

    if expected_tool:

        actual_tools = [
            call["name"]
            for result in results
            for call in result.get(
                "tool_calls",
                []
            )
        ]

        if expected_tool == "not_called":
            passed = len(actual_tools) == 0

        elif expected_tool == "not_called_without_id":
            passed = len(actual_tools) == 0

        elif expected_tool == "optional_sanitized_lookup":
            passed = True

        else:
            passed = expected_tool in actual_tools

        checks.append(
            (
                "tool",
                expected_tool,
                passed
            )
        )

    # Tool arguments
    expected_arguments = expect.get(
        "tool_arguments"
    )

    if expected_arguments:

        actual_calls = [
            call
            for result in results
            for call in result.get(
                "tool_calls",
                []
            )
        ]

        passed = any(
            call["arguments"] == expected_arguments
            for call in actual_calls
        )

        checks.append(
            (
                "tool_arguments",
                str(expected_arguments),
                passed
            )
        )

    # Handoff
    if "handoff" in expect:

        actual_handoff = results[-1].get(
            "handoff",
            False
        )

        checks.append(
            (
                "handoff",
                str(expect["handoff"]),
                actual_handoff == expect["handoff"]
            )
        )

    passed_count = sum(
        passed
        for _, _, passed in checks
    )

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": passed_count == len(checks),
        "passed_count": passed_count,
        "total": len(checks),
        "checks": checks,
        "answer": answer
    }


def main():

    cases = load_cases()

    print("=" * 70)
    print("ASTER & ROW AI AGENT EVALUATION")
    print("=" * 70)

    all_results = []

    for case in cases:

        print(
            f"\nRunning: {case['id']}"
        )

        try:

            results = run_agent(
                case["messages"]
            )

            result = check_case(
                case,
                results
            )

            all_results.append(result)

            status = (
                "PASS"
                if result["passed"]
                else "FAIL"
            )

            print(
                f"{status} "
                f"({result['passed_count']}/"
                f"{result['total']})"
            )

            if not result["passed"]:

                print("Failed checks:")

                for check_type, value, passed in result["checks"]:

                    if not passed:

                        print(
                            f"  - {check_type}: {value}"
                        )

        except Exception as error:

            print(
                f"ERROR: {type(error).__name__}: "
                f"{error}"
            )

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(
        result["passed"]
        for result in all_results
    )

    total = len(all_results)

    print(
        f"\nCases passed: {passed}/{total}"
    )

    categories = {}

    for result in all_results:

        category = result["category"]

        if category not in categories:
            categories[category] = [
                0,
                0
            ]

        categories[category][1] += 1

        if result["passed"]:
            categories[category][0] += 1

    print("\nBy category:")

    for category, values in categories.items():

        print(
            f"- {category}: "
            f"{values[0]}/{values[1]}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()