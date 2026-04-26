from server import (
    search_clinical_literature,
    search_public_discourse,
    analyze_semantic_gap,
    get_discourse_timeline
)

def test_clinical_tool():
    result = search_clinical_literature("dopamine reward", years_back=5)
    assert result is not None
    assert "Error" not in result
    assert len(result) > 100
    print("✓ clinical literature tool works")

def test_public_tool():
    result = search_public_discourse("dopamine", from_year=2018)
    assert result is not None
    assert "Error" not in result
    print("✓ public discourse tool works")

def test_gap_tool():
    result = analyze_semantic_gap(
        "dopamine reward prediction error",
        "dopamine hit wellness",
        "dopamine and motivation"
    )
    assert "CLINICAL LITERATURE" in result
    assert "PUBLIC DISCOURSE" in result
    print("✓ gap analysis tool works")

def test_timeline_tool():
    result = get_discourse_timeline("dopamine detox", 2015, 2020)
    assert "DISCOURSE TIMELINE" in result
    print("✓ timeline tool works")

if __name__ == "__main__":
    test_clinical_tool()
    test_public_tool()
    test_gap_tool()
    test_timeline_tool()
    print("\nAll tests passed.")