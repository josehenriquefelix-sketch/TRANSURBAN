CREATE UNIQUE INDEX `one_boarding_per_run` ON `boardings` (`user_id`,`run_id`);--> statement-breakpoint
CREATE UNIQUE INDEX `one_active_boarding_per_user` ON `boardings` (`user_id`) WHERE "boardings"."active" = 1;--> statement-breakpoint
CREATE UNIQUE INDEX `one_active_run_per_driver` ON `runs` (`driver_id`) WHERE "runs"."active" = 1;