# Prevents a class from having both ModernFulfillment and LegacyFulfillment
# anywhere in its ancestor chain.
class Rubydex::Linter::Rules::NoConflictingFulfillmentMixins < Rubydex::Linter::CustomRule
  def self.default_severity = Rubydex::Severity::Error

  def lint
    child_classes("ModernFulfillment").each do |declaration|
      next unless declaration.has_ancestor?("LegacyFulfillment")

      definition = declaration.definitions.first
      next unless definition

      add_diagnostic(
        "`#{declaration.name}` must not use both fulfillment implementations.",
        diagnostic_location(definition),
      )
    end
  end
end
