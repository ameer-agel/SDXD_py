-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: 01 يوليو 2026 الساعة 23:47
-- إصدار الخادم: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sdxd`
--

-- --------------------------------------------------------

--
-- بنية الجدول `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `id_number` varchar(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `admins`
--

INSERT INTO `admins` (`id`, `full_name`, `id_number`, `username`, `password`, `created_at`) VALUES
(1, 'samar alqadi', '44445555', 'maneger', 'maneger', '2026-06-30 08:10:29'),
(2, 'Administrator', '11112222', 'admin', 'admin123', '2026-07-22 17:09:00');

-- --------------------------------------------------------

--
-- بنية الجدول `ai_results`
--

CREATE TABLE `ai_results` (
  `result_id` int(11) NOT NULL,
  `scan_id` int(11) NOT NULL,
  `diagnosis_label` varchar(400) DEFAULT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  `findings_json` longtext DEFAULT NULL,
  `model_version` varchar(50) DEFAULT NULL,
  `processing_time_ms` int(11) DEFAULT NULL,
  `analyzed_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `doctor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `ai_results`
--

INSERT INTO `ai_results` (`result_id`, `scan_id`, `diagnosis_label`, `confidence_score`, `findings_json`, `model_version`, `processing_time_ms`, `analyzed_at`, `doctor_id`) VALUES
(4, 4, '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111222222222222222222222222222222222222222222222222222200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 85.50, NULL, 'v1.2', 120, '2026-06-25 13:07:07', 1),
(5, 10, 'Healthy', 92.00, NULL, 'v1.2', 110, '2026-06-25 13:07:07', 1),
(6, 12, 'Caries Detected', 78.40, NULL, 'v1.2', 135, '2026-06-25 13:07:07', 3),
(7, 13, 'Caries Detected', 89.50, NULL, 'v1.2', NULL, '2026-06-27 06:41:46', 3),
(8, 15, 'Caries Detected', 88.50, NULL, 'v1.2', 125, '2026-06-27 14:42:19', NULL),
(10, 16, 'Caries Detected', 88.50, NULL, 'v1.2', 125, '2026-06-27 14:42:47', NULL),
(11, 19, 'Healthy', 95.50, NULL, 'v1.2', 115, '2026-06-28 17:53:41', 3),
(12, 20, 'Caries Detected', 82.00, NULL, 'v1.2', 140, '2026-06-28 17:53:41', 3);

-- --------------------------------------------------------

--
-- بنية الجدول `appointments`
--

CREATE TABLE `appointments` (
  `appointment_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `preferred_date` date NOT NULL,
  `preferred_time` time NOT NULL,
  `treatment_type` varchar(150) DEFAULT NULL,
  `status` enum('pending','confirmed','completed','cancelled') DEFAULT 'pending',
  `patient_notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `appointment_type` enum('new_visit','follow_up') NOT NULL DEFAULT 'new_visit'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `appointments`
--

INSERT INTO `appointments` (`appointment_id`, `patient_id`, `doctor_id`, `preferred_date`, `preferred_time`, `treatment_type`, `status`, `patient_notes`, `created_at`, `updated_at`, `appointment_type`) VALUES
(1, 12, 3, '2026-07-05', '10:30:00', 'Dental Checkup', 'completed', 'First Visit', '2026-06-28 14:00:38', '2026-06-29 12:32:54', 'follow_up'),
(9, 13, 3, '2026-07-20', '09:26:00', NULL, 'completed', NULL, '2026-06-29 12:26:18', '2026-06-29 14:42:51', 'follow_up'),
(12, 13, 1, '2026-07-07', '12:40:00', NULL, 'cancelled', NULL, '2026-06-29 17:41:10', '2026-06-29 18:38:12', 'new_visit'),
(13, 13, 3, '2026-07-11', '13:51:00', NULL, 'cancelled', NULL, '2026-06-29 17:51:32', '2026-06-29 18:38:18', 'new_visit'),
(17, 12, 1, '2026-07-03', '13:48:00', NULL, 'pending', NULL, '2026-06-29 20:48:43', '2026-06-29 20:48:43', 'new_visit');

-- --------------------------------------------------------

--
-- بنية الجدول `clinical_notes`
--

CREATE TABLE `clinical_notes` (
  `note_id` int(11) NOT NULL,
  `scan_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `note_text` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `clinical_notes`
--

INSERT INTO `clinical_notes` (`note_id`, `scan_id`, `doctor_id`, `note_text`, `created_at`, `updated_at`) VALUES
(1, 20, 3, 'hjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj', '2026-06-29 07:02:46', '2026-06-29 07:02:46');

-- --------------------------------------------------------

--
-- بنية الجدول `doctors`
--

CREATE TABLE `doctors` (
  `doctor_id` int(10) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `last_name` varchar(100) NOT NULL,
  `idDoctor` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `specialty` varchar(150) DEFAULT NULL,
  `license_number` varchar(100) DEFAULT NULL,
  `clinic_name` varchar(200) DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `role` enum('admin','doctor') DEFAULT 'doctor',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ai_filter` varchar(255) DEFAULT NULL,
  `report_language` varchar(255) DEFAULT NULL,
  `enhancement_model` varchar(255) DEFAULT NULL,
  `two_factor_enabled` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `doctors`
--

INSERT INTO `doctors` (`doctor_id`, `first_name`, `email`, `last_name`, `idDoctor`, `password_hash`, `phone`, `specialty`, `license_number`, `clinic_name`, `profile_photo`, `role`, `is_active`, `created_at`, `updated_at`, `ai_filter`, `report_language`, `enhancement_model`, `two_factor_enabled`) VALUES
(1, 'Al-Mansoori', 'almansoori@sdxd-dental.com', 'alqadi', '4123567894', '12345678', '0599999999', 'طب اسنان', 'D-1548', 'Apex International Dental Center', 'images.jpg', 'doctor', 1, '2026-06-23 11:15:25', '2026-06-30 10:40:07', 'diffusion', 'en', NULL, 0),
(3, 'samar ', 'samarfouad@gmail.com', 'al qadi', '444411111', '123123123', '0599999999', '1', '1548', 'Apex International Dental Center', '444411111_444411111_444411111_444411111_images_1.jpg', 'doctor', 1, '2026-06-26 10:11:49', '2026-06-28 11:16:56', 'clahe', 'en', NULL, 0),
(4, 'فؤاد', 'samarfuoad185@gmail.com', 'القاضي', '44778899', '123456789', '05990599', 'طب اسنان', NULL, 'عيادة عطاء بلا حدود', NULL, 'doctor', 1, '2026-06-30 10:41:09', '2026-06-30 10:41:09', NULL, NULL, NULL, 0);

-- --------------------------------------------------------

--
-- بنية الجدول `patients`
--

CREATE TABLE `patients` (
  `patient_id` int(11) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `PatientId` varchar(10) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `emailP` varchar(255) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `registered_by` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `patients`
--

INSERT INTO `patients` (`patient_id`, `full_name`, `PatientId`, `phone`, `emailP`, `date_of_birth`, `gender`, `password_hash`, `registered_by`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'samar', '123456789', '11', 'samarfuoad185@gmail.com', '2026-06-24', NULL, 'scrypt:32768:8:1$y8OX7lwmAJrtip3S$8eca284f711b64efdebc2c8f38fcc082cb18a72a68ad9f260b885def9a23491e0d002f5ac346dfb2864ed661214c69bf370b918a601af217f0208d0c245ca165', NULL, 1, '2026-06-23 20:48:24', '2026-06-30 10:42:27'),
(2, 'سهير الثاضي ', '444411112', '0599904244', 'samarfuoad185@gmail.com', '2026-05-31', NULL, '444411111', NULL, 1, '2026-06-24 11:55:42', '2026-06-27 11:49:24'),
(10, 'فؤاد حسن عبدالله القاضي', '123123123', '0599904244', 'samarfuoad185@gmail.com', '2026-06-14', NULL, '123123123', NULL, 1, '2026-06-26 12:27:45', '2026-06-26 12:27:45'),
(11, 'فؤاد حسن عبدالله القاضي', '123456781', '0599904244', 'samarfuoad185@gmail.com', '2026-04-27', NULL, 'scrypt:32768:8:1$4TfBeaIMF6DI5Vik$177acc89c1bc3eb37d5226f22b7b8373a6b6d7118d1e19cebe15a7c1972e3ff561848b31f446c51d2c0b645139777dd16ac266e8b9a7456176f902a5ff951237', NULL, 1, '2026-06-26 12:51:54', '2026-06-26 12:51:54'),
(12, 'فؤاد حسن عبدالله القاضي', '444411222', '0599904244', 'samarfuoad185@gmail.com', '2026-07-01', NULL, 'scrypt:32768:8:1$EPs9UolZiIctAfBD$7947a4ffb19229004e974964bf17e4fa2efd6b2ca5af9a7a03d53f1858b563d6a7e3642e4794a06ec07faae3dd3e40d8fd89c685f51a62fee272d61ca87d3e49', NULL, 1, '2026-06-27 08:28:34', '2026-06-27 08:28:34'),
(13, 'samar al qadi', '444411133', '0599904244', 'samarfuoad185@gmail.com', '2026-06-16', NULL, 'scrypt:32768:8:1$4XXnNawidHgfsZpB$59c942da561a09c979240ec7b5b7c5dd9d9ff5524cbece5965e0d1e77417fa6b943125488e9a3abbcaf170afdb99040bcf39731d0a88bc1ce37a43f789cb52ec', NULL, 1, '2026-06-27 14:33:11', '2026-06-27 14:33:11'),
(14, 'أحمد محمد علي', '1122334455', '0590000000', 'ahmed@example.com', '1995-05-15', 'male', 'password123', 1, 1, '2026-06-27 14:40:49', '2026-06-27 14:40:49'),
(15, 'فؤاد حسن عبدالله القاضي', '444411111', '0599904244', 'samarfuoad185@gmail.com', '2026-06-11', NULL, 'scrypt:32768:8:1$JCifUDmLr7SKKZcm$995651e9d8d8b748331d776c5df18279c65b5c5a835ca4da3f7aaffb0a64dfb3d8973dfee6cc6ab37328a1f759fc810a6a9340cfb66e9ab0385aff09aad649ea', NULL, 1, '2026-06-28 11:12:20', '2026-06-28 11:12:20');

-- --------------------------------------------------------

--
-- بنية الجدول `scans`
--

CREATE TABLE `scans` (
  `scan_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `file_type` enum('jpg','png','dicom') DEFAULT 'jpg',
  `file_size_kb` int(11) DEFAULT NULL,
  `scan_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','processing','done','failed') DEFAULT 'pending',
  `notes` text DEFAULT NULL,
  `appointment_id` int(11) DEFAULT NULL,
  `scan_type` varchar(100) NOT NULL DEFAULT 'Dental X-Ray'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- إرجاع أو استيراد بيانات الجدول `scans`
--

INSERT INTO `scans` (`scan_id`, `patient_id`, `doctor_id`, `image_path`, `original_name`, `file_type`, `file_size_kb`, `scan_date`, `status`, `notes`, `appointment_id`, `scan_type`) VALUES
(1, 1, 1, 'uploads/test_xray.png', 'test_xray.png', 'png', 1024, '2026-06-24 12:22:43', 'done', 'Caries detected ', NULL, 'Dental X-Ray'),
(2, 1, 1, 'uploads/test_xray.png', 'test_xray.png', 'png', 1024, '2026-06-24 12:28:19', 'done', 'Caries detected ', NULL, 'Dental X-Ray'),
(3, 1, 1, 'uploads/test_xray.png', 'test_xray.png', 'png', 1024, '2026-06-24 12:30:46', 'done', 'Caries detected ', NULL, 'Dental X-Ray'),
(4, 1, 1, 'uploads/test_xray.png', 'test_xray.png', 'png', 1024, '2026-06-24 12:33:26', 'pending', 'Caries detected ', NULL, 'Dental X-Ray'),
(6, 2, 1, 'uploads/test_xray.png', 'test_xray.png', 'png', 1024, '2026-06-24 12:36:20', 'pending', 'Caries detected ', NULL, 'Dental X-Ray'),
(9, 1, 1, '', NULL, 'jpg', NULL, '2026-06-24 12:30:00', 'done', 'Regular checkup', NULL, 'Dental X-Ray'),
(10, 2, 3, 'uploads/test_xray.png', NULL, 'jpg', NULL, '2026-06-24 12:36:00', 'pending', 'ggggggggggggggggggg', NULL, 'Dental X-Ray'),
(11, 1, 1, '', NULL, 'jpg', NULL, '2026-06-24 12:30:00', 'done', 'Regular checkup', NULL, 'Dental X-Ray'),
(12, 2, 3, '', NULL, 'jpg', NULL, '2026-06-24 12:36:00', 'pending', 'Lower molar pain', NULL, 'Dental X-Ray'),
(13, 1, 3, 'uploads/scan_001.png', 'scan_001.png', 'png', 1024, '2026-06-27 06:37:48', 'pending', 'فحص جديد تمت إضافته بواسطة النظام للطبيبة سمر', NULL, 'Dental X-Ray'),
(14, 2, 3, 'uploads/new_test.png', 'new_test.png', 'png', NULL, '2026-06-27 06:41:46', 'done', 'فحص تجريبي جديد لسهير', NULL, 'Dental X-Ray'),
(15, 12, 3, 'test_xray', 'scan_test.png', 'png', 1024, '2026-06-27 14:41:55', 'pending', 'فحص تجريبي جديد', NULL, 'Dental X-Ray'),
(16, 12, 3, 'uploads/new_scan_test.png', 'scan_test.png', 'png', 1024, '2026-06-27 14:42:19', 'pending', 'فحص تجريبي جديد', NULL, 'Dental X-Ray'),
(17, 12, 1, 'uploads/new_scan_test.png', 'scan_test.png', 'png', 1024, '2026-06-27 14:42:27', 'pending', 'فحص تجريبي جديد', NULL, 'Dental X-Ray'),
(18, 13, 1, 'uploads/new_scan_test.png', 'scan_test.png', 'png', 1024, '2026-06-27 14:42:47', 'pending', 'فحص تجريبي جديد', NULL, 'Dental X-Ray'),
(19, 12, 3, 'images2.jpg', 'test.png', 'png', 980, '2026-06-28 14:01:06', 'done', 'Dental X-Ray', 1, 'Dental X-Ray'),
(20, 13, 3, 'images2.jpg', 'patient13_scan.png', 'png', 1024, '2026-06-28 14:07:57', 'done', 'فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13فحnnnnnnnnnnnnnnnnnnnnnnصllllllllllllll تجريبي للمريض 13', NULL, 'Dental X-Ray');

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_dashboard_stats`
-- (See below for the actual view)
--
CREATE TABLE `v_dashboard_stats` (
`total_scans` bigint(21)
,`active_patients` bigint(21)
,`reports_today` bigint(21)
,`avg_ai_accuracy` decimal(5,1)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_scan_summary`
-- (See below for the actual view)
--
CREATE TABLE `v_scan_summary` (
`scan_id` int(11)
,`doctor_id` int(11)
,`PatientId` varchar(10)
,`patient_name` varchar(200)
,`scan_date` timestamp
,`status` enum('pending','processing','done','failed')
,`notes` text
,`diagnosis_label` varchar(400)
,`confidence_score` decimal(5,2)
);

-- --------------------------------------------------------

--
-- Structure for view `v_dashboard_stats`
--
DROP TABLE IF EXISTS `v_dashboard_stats`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_dashboard_stats`  AS SELECT count(distinct `s`.`scan_id`) AS `total_scans`, count(distinct `s`.`patient_id`) AS `active_patients`, count(distinct case when cast(`s`.`scan_date` as date) = curdate() then `s`.`scan_id` end) AS `reports_today`, round(avg(`r`.`confidence_score`),1) AS `avg_ai_accuracy` FROM (`scans` `s` left join `ai_results` `r` on(`s`.`scan_id` = `r`.`scan_id`)) ;

-- --------------------------------------------------------

--
-- Structure for view `v_scan_summary`
--
DROP TABLE IF EXISTS `v_scan_summary`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_scan_summary`  AS SELECT `s`.`scan_id` AS `scan_id`, `s`.`doctor_id` AS `doctor_id`, `p`.`PatientId` AS `PatientId`, `p`.`full_name` AS `patient_name`, `s`.`scan_date` AS `scan_date`, `s`.`status` AS `status`, `s`.`notes` AS `notes`, `ar`.`diagnosis_label` AS `diagnosis_label`, `ar`.`confidence_score` AS `confidence_score` FROM ((`scans` `s` join `patients` `p` on(`s`.`patient_id` = `p`.`patient_id`)) left join `ai_results` `ar` on(`s`.`scan_id` = `ar`.`scan_id`)) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_number` (`id_number`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `ai_results`
--
ALTER TABLE `ai_results`
  ADD PRIMARY KEY (`result_id`),
  ADD UNIQUE KEY `scan_id` (`scan_id`),
  ADD KEY `fk_ai_doctor` (`doctor_id`);

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`appointment_id`),
  ADD UNIQUE KEY `unique_doctor_slot` (`doctor_id`,`preferred_date`,`preferred_time`),
  ADD KEY `idx_appt_patient` (`patient_id`),
  ADD KEY `idx_appt_date` (`preferred_date`);

--
-- Indexes for table `clinical_notes`
--
ALTER TABLE `clinical_notes`
  ADD PRIMARY KEY (`note_id`),
  ADD KEY `fk_note_scan` (`scan_id`),
  ADD KEY `fk_note_doctor` (`doctor_id`);

--
-- Indexes for table `doctors`
--
ALTER TABLE `doctors`
  ADD PRIMARY KEY (`doctor_id`),
  ADD UNIQUE KEY `email` (`idDoctor`);

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`patient_id`),
  ADD UNIQUE KEY `email` (`PatientId`),
  ADD KEY `fk_patient_doctor` (`registered_by`);

--
-- Indexes for table `scans`
--
ALTER TABLE `scans`
  ADD PRIMARY KEY (`scan_id`),
  ADD KEY `idx_scans_patient` (`patient_id`),
  ADD KEY `idx_scans_doctor` (`doctor_id`),
  ADD KEY `idx_scans_status` (`status`),
  ADD KEY `fk_scan_appointment` (`appointment_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `ai_results`
--
ALTER TABLE `ai_results`
  MODIFY `result_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `appointment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `clinical_notes`
--
ALTER TABLE `clinical_notes`
  MODIFY `note_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `doctors`
--
ALTER TABLE `doctors`
  MODIFY `doctor_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `patients`
--
ALTER TABLE `patients`
  MODIFY `patient_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `scans`
--
ALTER TABLE `scans`
  MODIFY `scan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- قيود الجداول المُلقاة.
--

--
-- قيود الجداول `ai_results`
--
ALTER TABLE `ai_results`
  ADD CONSTRAINT `fk_ai_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_result_scan` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- قيود الجداول `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `fk_appt_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_appt_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;

--
-- قيود الجداول `clinical_notes`
--
ALTER TABLE `clinical_notes`
  ADD CONSTRAINT `fk_note_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_note_scan` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- قيود الجداول `patients`
--
ALTER TABLE `patients`
  ADD CONSTRAINT `fk_patient_doctor` FOREIGN KEY (`registered_by`) REFERENCES `doctors` (`doctor_id`) ON DELETE SET NULL;

--
-- قيود الجداول `scans`
--
ALTER TABLE `scans`
  ADD CONSTRAINT `fk_scan_appointment` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`appointment_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_scan_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_scan_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
