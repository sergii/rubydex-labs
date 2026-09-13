module Reports
  class CaptureJob < ApplicationJob
    queue_as :reports

    def perform(report_id)
      report_id
    end
  end
end
