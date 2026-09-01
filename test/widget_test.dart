import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:miner_repair_diagnostic_assistant/main.dart';

void main() {
  testWidgets('Miner Repair App initialization smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: MinerRepairApp(),
      ),
    );

    // Let any scheduled frames compile
    await tester.pumpAndSettle();

    // Verify that the App Bar title is displayed
    expect(find.text('اسکنر شبکه ماینرها'), findsOneWidget);

    // Verify that our Bottom Navigation Bar tabs are present
    expect(find.text('اسکنر شبکه'), findsOneWidget);
    expect(find.text('عیب‌یابی AI'), findsOneWidget);
    expect(find.text('دانشنامه خطا'), findsOneWidget);

    // Tap on the 'دانشنامه خطا' tab and trigger a frame.
    await tester.tap(find.text('دانشنامه خطا'));
    await tester.pumpAndSettle();

    // Verify we transitioned successfully to the Repair Knowledge Base page
    expect(find.text('کدهای خطا Antminer'), findsOneWidget);
  });
}
